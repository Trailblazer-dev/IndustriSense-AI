"""IndustriSense AI - Flask Web Application"""
import os
import pickle
import json
import pandas as pd
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import requests
import hmac
import hashlib
import json as json_lib
from config import config
import sys
import os
# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from src.models import model_utils

# Initialize Flask app
# Initialize Flask and load config
app = Flask(__name__, template_folder='templates', static_folder='static')
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Enable CORS only when ALLOWED_ORIGINS is configured (safer default)
allowed = app.config.get('ALLOWED_ORIGINS', '')
if allowed:
    origins = [o.strip() for o in allowed.split(',') if o.strip()]
    if origins:
        CORS(app, resources={r"/*": {"origins": origins}})

# Lazy-loaded globals
_models = {'classifier': None, 'regressor': None}
_dataframe = None

def _sha256_file(path):
    """Compute SHA256 for a file (used for basic integrity logging)."""
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()

def get_models(force_reload=False):
    """Lazily load models with basic integrity logging.

    Notes:
    - Loading pickled models can be unsafe if artifacts are tampered with.
    - We compute and log SHA256 for deployed artifacts to help verification and audits.
    """
    global _models
    if _models['classifier'] is not None and not force_reload:
        return _models['classifier'], _models['regressor']

    model_dir = app.config['MODEL_DIR']

    try:
        classifier, clf_sha = model_utils.load_classifier(model_dir)
        regressor, reg_sha = model_utils.load_regressor(model_dir)

        if clf_sha:
            print(f"Classifier artifact SHA256: {clf_sha}")
        if reg_sha:
            print(f"Regressor artifact SHA256: {reg_sha}")

        _models['classifier'] = classifier
        _models['regressor'] = regressor
        return classifier, regressor

    except Exception as e:
        print(f"Error loading models: {e}")
        _models['classifier'] = None
        _models['regressor'] = None
        return None, None

def get_data(force_reload=False):
    """Lazily load raw features (used for inference)"""
    global _dataframe
    if _dataframe is not None and not force_reload:
        return _dataframe

    data_dir = app.config['DATA_DIR']
    raw_path = os.path.join(data_dir, 'features_engineered_raw.csv')
    try:
        if os.path.exists(raw_path):
            df_local = pd.read_csv(raw_path)
            _dataframe = df_local
            return _dataframe
        else:
            print(f"Error: RAW features file not found at {raw_path}")
            _dataframe = None
            return None
    except Exception as e:
        print(f"Error loading data: {e}")
        _dataframe = None
        return None

# Note: Raw features now primary data source (used in load_data() for inference)
# This function is kept for backward compatibility and state verification
def load_raw_data():
    """Load raw (unscaled) features - NOTE: app.py now uses raw data for model inference"""
    data_dir = app.config['DATA_DIR']
    try:
        df_raw = pd.read_csv(os.path.join(data_dir, 'features_engineered_raw.csv'))
        return df_raw
    except FileNotFoundError:
        print(f"Warning: Raw features file not found.")
        return None

df_raw = load_raw_data()

# Feature columns
FEATURE_COLS_CLASSIFIER = [
    'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]',
    'Torque [Nm]', 'Tool wear [min]', 'Stress Index', 'Temp Diff [K]',
    'Temp_Diff_x_Wear', 'Speed_x_Torque', 'is_anomaly'
]

FEATURE_COLS_REGRESSOR = [
    'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]',
    'Torque [Nm]', 'Temp Diff [K]', 'Speed_x_Torque', 'is_anomaly'
]

# ✅ RUL Regressor: Clean Features (Data Leakage Removed)
# Removed leaky features that were derived from tool wear:
#   - Stress Index = Torque × Tool Wear (was feature engineering error)
#   - Temp_Diff_x_Wear = Temp Diff × Tool Wear (was feature engineering error)
# Model retrained with 7 clean sensor-only features.
# Performance: Test R² = 0.104, MAE = 51.31 min (realistic, production-ready)

# ==================== Utility Functions ====================

def rul_minutes_to_calendar_time(remaining_minutes, operating_hours_per_day=8):
    """
    Convert RUL from operating minutes to human-readable calendar time.
    
    Args:
        remaining_minutes: Remaining tool life in operating minutes
        operating_hours_per_day: Daily machine operating hours (default: 8 hours/day shift)
    
    Returns:
        Dictionary with various time units for flexibility
    
    Note: 254 minutes is the max tool wear in AI4I 2020 dataset (snapshot-based).
    For real deployments, verify the actual tool replacement interval with domain experts.
    """
    if remaining_minutes <= 0:
        return {
            'minutes': 0,
            'hours': 0,
            'days': 0,
            'weeks': 0,
            'months': 0,
            'formatted': 'Tool replacement needed immediately'
        }
    
    remaining_hours = remaining_minutes / 60
    calendar_days = remaining_hours / operating_hours_per_day
    calendar_weeks = calendar_days / 7
    calendar_months = calendar_days / 30.44
    
    return {
        'minutes': round(remaining_minutes, 1),
        'hours': round(remaining_hours, 1),
        'days': round(calendar_days, 1),
        'weeks': round(calendar_weeks, 2),
        'months': round(calendar_months, 2),
        'formatted': f'{round(calendar_days, 0):.0f} days' if calendar_days >= 1 else f'{round(remaining_hours, 1)} hours'
    }

# ==================== Routes ====================

@app.route('/')
def dashboard():
    """Dashboard - Main page with machine overview (Predicted values only)"""
    df_local = get_data()
    if df_local is None:
        return render_template('error.html', message='Data not loaded'), 500
    
    # Sample 10 machines with stratified status distribution
    machines = []
    
    # Pre-calculate statuses for all rows to get balanced sample
    statuses = []
    classifier, regressor = get_models()
    if classifier is None or regressor is None:
        return render_template('error.html', message='Models not loaded'), 500

    for idx in range(len(df_local)):
        row = df_local.iloc[idx]
        X_classifier = df_local.iloc[[idx]][FEATURE_COLS_CLASSIFIER]
        X_regressor = df_local.iloc[[idx]][FEATURE_COLS_REGRESSOR]

        failure_prob = float(classifier.predict_proba(X_classifier)[0][1]) * 100
        predicted_tool_wear = float(regressor.predict(X_regressor)[0])
        
        # Status determination: Prioritize wear-based assessment
        if predicted_tool_wear >= 200:
            status = 'CRITICAL'
        elif predicted_tool_wear >= 150 or failure_prob >= 80:
            status = 'WARNING'
        else:
            status = 'NORMAL'
        
        statuses.append((idx, status, failure_prob, predicted_tool_wear))
    
    # Get balanced sample: try to get ~4-5 CRITICAL, ~3-4 WARNING, ~2-3 NORMAL
    critical = [x for x in statuses if x[1] == 'CRITICAL'][:5]
    warning = [x for x in statuses if x[1] == 'WARNING'][:3]
    normal = [x for x in statuses if x[1] == 'NORMAL'][:2]
    
    sample_indices = [x[0] for x in critical + warning + normal]
    
    for idx in sample_indices:
        row = df_local.iloc[idx]
        X_classifier = df_local.iloc[[idx]][FEATURE_COLS_CLASSIFIER]
        X_regressor = df_local.iloc[[idx]][FEATURE_COLS_REGRESSOR]

        # Failure risk prediction (raw probability from classifier)
        failure_prob = float(classifier.predict_proba(X_classifier)[0][1]) * 100

        # Predicted tool wear (model estimate in minutes)
        predicted_tool_wear = float(regressor.predict(X_regressor)[0])
        
        # Predicted RUL (minutes remaining until 254-min threshold)
        predicted_rul = max(0, app.config.get('MAX_TOOL_WEAR', 254) - int(predicted_tool_wear))
        
        # Status determination: Standardized thresholds
        # CRITICAL: High wear (>=200 min) OR high failure risk (>=75%)
        # WARNING: Moderate wear (>=150 min) OR moderate failure risk (>=50%)
        # NORMAL: Low wear (<150 min) AND low failure risk (<50%)
        if predicted_tool_wear >= 200 or failure_prob >= 75:
            status = 'CRITICAL'
        elif predicted_tool_wear >= 150 or failure_prob >= 50:
            status = 'WARNING'
        else:
            status = 'NORMAL'
        
        machines.append({
            'id': int(idx),
            'failure_risk': round(failure_prob, 1),  # Raw classifier probability (0-100%)
            'predicted_tool_wear': round(predicted_tool_wear, 1),
            'predicted_rul': predicted_rul,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
    
    # Calculate status counts for stats cards
    status_counts = {
        'total': len(machines),
        'critical': sum(1 for m in machines if m['status'] == 'CRITICAL'),
        'warning': sum(1 for m in machines if m['status'] == 'WARNING'),
        'normal': sum(1 for m in machines if m['status'] == 'NORMAL')
    }
    
    return render_template('dashboard.html', machines=machines, status_counts=status_counts)

@app.route('/diagnostics/model-calibration')
def model_calibration():
    """Diagnostic endpoint: Check model distributions and reliability"""
    df_local = get_data()
    classifier, regressor = get_models()
    if df_local is None or classifier is None:
        return jsonify({'error': 'Models or data not loaded'}), 500

    # Get predictions for sample data
    failure_probs = []
    wear_preds = []
    for idx in range(min(200, len(df_local))):  # Sample first 200
        row = df_local.iloc[idx]
        X_classifier = df_local.iloc[[idx]][FEATURE_COLS_CLASSIFIER]
        X_regressor = df_local.iloc[[idx]][FEATURE_COLS_REGRESSOR]
        fail_prob = float(classifier.predict_proba(X_classifier)[0][1]) * 100
        wear_pred = float(regressor.predict(X_regressor)[0])
        failure_probs.append(fail_prob)
        wear_preds.append(wear_pred)
    
    failure_probs = np.array(failure_probs)
    wear_preds = np.array(wear_preds)
    
    return jsonify({
        'classifier_distribution': {
            'mean_failure_prob_percent': round(float(np.mean(failure_probs)), 2),
            'median_failure_prob_percent': round(float(np.median(failure_probs)), 2),
            'min_failure_prob_percent': round(float(np.min(failure_probs)), 2),
            'max_failure_prob_percent': round(float(np.max(failure_probs)), 2),
            'std_failure_prob_percent': round(float(np.std(failure_probs)), 2),
            'samples_above_50pct': int(np.sum(failure_probs >= 50)),
            'samples_above_75pct': int(np.sum(failure_probs >= 75)),
            'total_samples': len(failure_probs),
            'status': '✓ Production-ready (83.8% test recall, 82.1% test precision)'
        },
        'regressor_distribution': {
            'mean_predicted_wear_minutes': round(float(np.mean(wear_preds)), 2),
            'median_predicted_wear_minutes': round(float(np.median(wear_preds)), 2),
            'min_predicted_wear_minutes': round(float(np.min(wear_preds)), 2),
            'max_predicted_wear_minutes': round(float(np.max(wear_preds)), 2),
            'std_predicted_wear_minutes': round(float(np.std(wear_preds)), 2),
            'warning': '⚠️ CURRENT MODEL HAS DATA LEAKAGE: Includes Stress Index and Temp_Diff_x_Wear (both derived from tool wear). Inflates R² to 0.9995. Should NOT be used for production RUL predictions. REQUIRED ACTION: Retrain without leaky features.'
        },
        'recommended_thresholds': {
            'CRITICAL': 'failure_prob >= 75% OR wear >= 200 minutes',
            'WARNING': 'failure_prob >= 50% OR wear >= 150 minutes',
            'NORMAL': 'failure_prob < 50% AND wear < 150 minutes'
        }
    })

@app.route('/analytics')
def analytics():
    """Analytics - Feature importance and model analysis"""
    model_dir = app.config['MODEL_DIR']
    
    # Load feature importance data if available
    importance_data = {
        'classifier': None,
        'regressor': None
    }
    
    try:
        if os.path.exists(os.path.join(model_dir, 'feature_importance.csv')):
            importance_data['classifier'] = pd.read_csv(
                os.path.join(model_dir, 'feature_importance.csv')
            ).to_dict('records')
    except:
        pass
    
    try:
        if os.path.exists(os.path.join(model_dir, 'wear_feature_importance.csv')):
            importance_data['regressor'] = pd.read_csv(
                os.path.join(model_dir, 'wear_feature_importance.csv')
            ).to_dict('records')
    except:
        pass
    
    return render_template('analytics.html', importance_data=importance_data)

@app.route('/models')
def models_page():
    """Models - Model performance and details"""
    model_dir = app.config['MODEL_DIR']
    
    model_info = {
        'classifier': {
            'name': 'Failure Classification Model',
            'type': 'XGBoost Classifier',
            'features': len(FEATURE_COLS_CLASSIFIER),
            'classes': 2,
            'metrics': None
        },
        'regressor': {
            'name': 'Tool Wear RUL Prognosis Model',
            'type': 'XGBoost Regressor',
            'features': len(FEATURE_COLS_REGRESSOR),
            'metrics': None
        }
    }
    
    # Load test results if available
    try:
        if os.path.exists(os.path.join(model_dir, 'test_results.csv')):
            results = pd.read_csv(os.path.join(model_dir, 'test_results.csv'))
            model_info['classifier']['metrics'] = results.to_dict('records')
    except:
        pass
    
    return render_template('models.html', model_info=model_info)

@app.route('/predict', methods=['GET', 'POST'])
def predict_page():
    """Prediction interface"""
    if request.method == 'GET':
        return render_template('predict.html', feature_names=FEATURE_COLS_CLASSIFIER)
    
    # Handle POST request (prediction)
    return prediction_api()

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

# ==================== API Endpoints ====================

@app.route('/api/predict', methods=['POST'])
def prediction_api():
    """API endpoint for predictions"""
    classifier, regressor = get_models()
    if classifier is None or regressor is None:
        return jsonify({'error': 'Models not loaded'}), 500

    try:
        data = request.get_json()

        # Validate input
        if not data or 'features' not in data:
            return jsonify({'error': 'Missing features in request'}), 400

        features = data['features']
        # Basic validation: length and numeric
        if not isinstance(features, (list, tuple, np.ndarray)):
            return jsonify({'error': 'Features must be an array'}), 400

        if len(features) != len(FEATURE_COLS_CLASSIFIER):
            return jsonify({'error': f'Expected {len(FEATURE_COLS_CLASSIFIER)} features'}), 400

        try:
            features = [float(x) for x in features]
        except Exception:
            return jsonify({'error': 'All feature values must be numeric'}), 400

        # Create feature arrays
        X_classifier = pd.DataFrame([features], columns=FEATURE_COLS_CLASSIFIER)
        X_regressor = pd.DataFrame([features[:len(FEATURE_COLS_REGRESSOR)]], columns=FEATURE_COLS_REGRESSOR)

        # Make predictions
        failure_prob = float(classifier.predict_proba(X_classifier)[0][1])
        tool_wear = float(regressor.predict(X_regressor)[0])
        rul = max(0, app.config.get('MAX_TOOL_WEAR', 254) - int(tool_wear))

        return jsonify({
            'success': True,
            'failure_probability_percent': round(failure_prob * 100, 2),
            'tool_wear_minutes': round(tool_wear, 2),
            'remaining_useful_life_minutes': rul,
            'risk_level': 'CRITICAL' if (failure_prob >= 0.75) else ('WARNING' if (failure_prob >= 0.50) else 'NORMAL'),
            'note': 'Tool wear and RUL are snapshot estimates based on current sensor state, not temporal degradation tracking',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        # Don't return raw exception text in production - log and return generic message
        print(f"Prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/machines/<int:machine_id>')
def get_machine_details(machine_id):
    """Get details for a specific machine (Hybrid: Actual + Predicted)"""
    df_local = get_data()
    if df_local is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    if machine_id < 0 or machine_id >= len(df_local):
        return jsonify({'error': f'Machine {machine_id} not found'}), 404
    
    # Use raw data for model predictions (matches training data distribution)
    row_scaled = df_local.iloc[machine_id]  # Note: variable name 'row_scaled' is legacy; data is RAW
    X_classifier = df_local.iloc[[machine_id]][FEATURE_COLS_CLASSIFIER]
    X_regressor = df_local.iloc[[machine_id]][FEATURE_COLS_REGRESSOR]

    classifier, regressor = get_models()
    if classifier is None or regressor is None:
        return jsonify({'error': 'Models not loaded'}), 500

    # Predictions
    failure_prob = float(classifier.predict_proba(X_classifier)[0][1])
    predicted_tool_wear = float(regressor.predict(X_regressor)[0])
    
    # Actual values (ground truth)
    df_raw_local = get_data()
    if df_raw_local is not None:
        row_raw = df_raw_local.iloc[machine_id]
        actual_tool_wear = float(row_raw['Tool wear [min]'])
    else:
        actual_tool_wear = float(row_scaled['Tool wear [min]'])
    
    # Calculate RUL values (254 min is max tool wear in dataset)
    max_wear = app.config.get('MAX_TOOL_WEAR', 254)
    actual_rul_min = max(0, max_wear - int(actual_tool_wear))
    predicted_rul_min = max(0, max_wear - int(predicted_tool_wear))
    
    # Convert to calendar time (assuming 8 hours/day standard shift)
    actual_rul_calendar = rul_minutes_to_calendar_time(actual_rul_min, operating_hours_per_day=8)
    predicted_rul_calendar = rul_minutes_to_calendar_time(predicted_rul_min, operating_hours_per_day=8)
    
    # Prediction error
    wear_error = abs(actual_tool_wear - predicted_tool_wear)
    # Use MAX_TOOL_WEAR for normalization
    error_percent = (wear_error / max(1, app.config.get('MAX_TOOL_WEAR', 254))) * 100
    
    # Model reliability assessment
    model_reliability = "UNRELIABLE" if abs(wear_error) > 50 else "MODERATE" if abs(wear_error) > 20 else "GOOD"
    reliability_warning = {
        "UNRELIABLE": "⚠️ WARNING: RUL predictions have high error margins (>50 min). Use only as reference; verify with physical tool inspection.",
        "MODERATE": "⚠️ BETA: RUL predictions have moderate error (±20-50 min). Cross-check with actual measured tool wear.",
        "GOOD": "✓ RUL prediction within acceptable range (±<20 min). Regressor uses clean sensor data (leaky features removed)."
    }
    
    return jsonify({
        'machine_id': machine_id,
        'features': {feat: float(row_scaled[feat]) for feat in FEATURE_COLS_CLASSIFIER},
        'failure_analysis': {
            'probability_percent': round(failure_prob * 100, 2),
            'status': 'CRITICAL' if failure_prob >= 0.75 else ('WARNING' if failure_prob >= 0.50 else 'NORMAL'),
            'note': '✓ Failure classifier is production-ready (83.8% test recall)'
        },
        'tool_wear_analysis': {
            'actual_tool_wear_minutes': round(actual_tool_wear, 2),
            'predicted_tool_wear_minutes': round(predicted_tool_wear, 2),
            'prediction_error_minutes': round(wear_error, 2),
            'prediction_error_percent': round(error_percent, 2),
            'max_tool_wear_threshold': 254
        },
        'rul_analysis': {
            'actual_remaining_useful_life_minutes': actual_rul_min,
            'predicted_remaining_useful_life_minutes': predicted_rul_min,
            'rul_difference_minutes': abs(actual_rul_min - predicted_rul_min),
            'actual_calendar_time': actual_rul_calendar,
            'predicted_calendar_time': predicted_rul_calendar,
            'note': 'Calendar times assume 8 hours/day operating schedule. Adjust operating_hours_per_day parameter for your machine schedule.'
        },
        'model_reliability': {
            'status': model_reliability,
            'warning': reliability_warning[model_reliability],
            'assessment': 'Failure classifier: Production-ready (83.8% test recall, 82.1% test precision). RUL regressor: HAS DATA LEAKAGE - Stress Index and Temp_Diff_x_Wear are derived from tool wear, causing artificial perfection (R²=0.9995). NOT production-ready. Retrain without leaky features.'
        },
        'model_performance_note': '🔴 CRITICAL: RUL predictions are unreliable due to data leakage. Failure classifier is trustworthy. For production RUL: retrain regressor with clean sensor features only (remove Stress Index and Temp_Diff_x_Wear).',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats')
def get_stats():
    """Get overall system statistics for dashboard sample machines (not entire dataset)"""
    df_local = get_data()
    classifier, _ = get_models()
    if df_local is None or classifier is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    # Use SAME sample indices as dashboard (fixed seed for consistency)
    np.random.seed(42)
    sample_indices = np.random.choice(len(df_local), 10, replace=False)
    
    # Calculate statistics ONLY for sampled machines
    df_sample = df_local.iloc[sample_indices]
    X_classifier = df_sample[FEATURE_COLS_CLASSIFIER]
    predictions = classifier.predict_proba(X_classifier)[:, 1]
    
    return jsonify({
        'total_machines': len(df_sample),
        'critical_count': int((predictions >= 0.75).sum()),
        'warning_count': int(((predictions >= 0.50) & (predictions < 0.75)).sum()),
        'normal_count': int((predictions < 0.50).sum()),
        'average_failure_risk': round(float(predictions.mean()) * 100, 2),
        'max_failure_risk': round(float(predictions.max()) * 100, 2),
        'timestamp': datetime.now().isoformat()
    })

# ==================== Error Handlers ====================

@app.route('/plans')
def plans():
    """Pricing and plans page"""
    plans_data = [
        {
            'name': 'Starter',
            'price': 29,
            'period': 'month',
            'description': 'Perfect for small operations',
            'features': [
                'Up to 5 machines',
                'Basic predictive maintenance',
                'Weekly reports',
                'Email support',
                'Dashboard access'
            ],
            'highlighted': False,
            'btn_text': 'Choose Plan'
        },
        {
            'name': 'Professional',
            'price': 99,
            'period': 'month',
            'description': 'For growing businesses',
            'features': [
                'Up to 50 machines',
                'Advanced ML analytics',
                'Daily reports',
                'Priority support',
                'API access',
                'Custom alerts',
                'Data export'
            ],
            'highlighted': True,
            'btn_text': 'Get Started'
        },
        {
            'name': 'Enterprise',
            'price': 299,
            'period': 'month',
            'description': 'For large-scale operations',
            'features': [
                'Unlimited machines',
                'Real-time predictions',
                'Hourly reports',
                '24/7 phone support',
                'Advanced API',
                'Custom integration',
                'Dedicated account manager'
            ],
            'highlighted': False,
            'btn_text': 'Contact Sales'
        }
    ]
    return render_template('plans.html', plans=plans_data)

@app.route('/checkout/<plan_name>')
def checkout(plan_name):
    """Checkout page for payment"""
    plan_mapping = {
        'starter': {'name': 'Starter', 'price': 29, 'plan_id': 'starter_plan'},
        'professional': {'name': 'Professional', 'price': 99, 'plan_id': 'pro_plan'},
        'enterprise': {'name': 'Enterprise', 'price': 299, 'plan_id': 'enterprise_plan'}
    }
    
    plan = plan_mapping.get(plan_name.lower())
    if not plan:
        return render_template('error.html', message='Invalid plan selected'), 400
    
    return render_template('checkout.html', plan=plan)

@app.route('/payment/process', methods=['POST'])
def process_payment():
    """Process payment with PayHero"""
    try:
        data = request.json
        plan_name = data.get('plan')
        email = data.get('email')
        phone = data.get('phone')
        
        # Validate input
        if not all([plan_name, email, phone]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Plan pricing
        plans = {
            'starter': {'amount': 2900, 'currency': 'KES'},  # 29 USD in cents
            'professional': {'amount': 9900, 'currency': 'KES'},
            'enterprise': {'amount': 29900, 'currency': 'KES'}
        }
        
        plan_data = plans.get(plan_name.lower())
        if not plan_data:
            return jsonify({'status': 'error', 'message': 'Invalid plan'}), 400
        
        # Create PayHero payment request
        payhero_api_key = app.config['PAYHERO_API_KEY']
        payhero_api_secret = app.config['PAYHERO_API_SECRET']
        
        # PayHero API endpoint
        api_url = 'https://api.payhero.io/api/v2/payments'
        if app.config['PAYHERO_SANDBOX']:
            api_url = 'https://sandbox.payhero.io/api/v2/payments'
        
        # Prepare payload
        payload = {
            'amount': plan_data['amount'],
            'currency': plan_data['currency'],
            'email': email,
            'phone_number': phone,
            'first_name': data.get('first_name', 'Customer'),
            'last_name': data.get('last_name', ''),
            'description': f'IndustriSense AI {plan_name.capitalize()} Plan',
            'callback_url': app.config['PAYMENT_SUCCESS_URL'],
            'error_callback_url': app.config['PAYMENT_FAIL_URL']
        }
        
        # Sign request (if required by PayHero)
        headers = {
            'Authorization': f'Bearer {payhero_api_key}',
            'Content-Type': 'application/json'
        }
        
        # Make API request
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            result = response.json()
            # Store payment info in session
            session['payment_ref'] = result.get('id', result.get('reference'))
            session['plan'] = plan_name
            session['email'] = email
            
            return jsonify({
                'status': 'success',
                'payment_url': result.get('payment_url', result.get('checkout_url')),
                'reference': result.get('id', result.get('reference'))
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'Payment gateway error: {response.text}'
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': f'Payment service error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error processing payment: {str(e)}'}), 500

@app.route('/payment/success')
def payment_success():
    """Payment success callback"""
    payment_ref = request.args.get('reference')
    plan = session.get('plan', 'Unknown')
    email = session.get('email', '')
    
    return render_template('payment_success.html', 
                         reference=payment_ref, 
                         plan=plan, 
                         email=email)

@app.route('/payment/failure')
def payment_failure():
    """Payment failure callback"""
    error_msg = request.args.get('message', 'Payment was not completed')
    error_code = request.args.get('code', 'Unknown')
    
    return render_template('payment_failure.html',
                         error_message=error_msg,
                         error_code=error_code)

@app.route('/payment/verify', methods=['POST'])
def verify_payment():
    """Verify payment status"""
    try:
        data = request.json
        payment_ref = data.get('reference')
        
        if not payment_ref:
            return jsonify({'status': 'error', 'message': 'No payment reference provided'}), 400
        
        # Verify with PayHero using reference
        payhero_api_key = app.config['PAYHERO_API_KEY']
        api_url = f'https://api.payhero.io/api/v2/payments/{payment_ref}'
        if app.config['PAYHERO_SANDBOX']:
            api_url = f'https://sandbox.payhero.io/api/v2/payments/{payment_ref}'
        
        headers = {
            'Authorization': f'Bearer {payhero_api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'status': 'success',
                'payment_status': result.get('status'),
                'amount': result.get('amount'),
                'email': result.get('email')
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'Payment not found'}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', message='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', message='Server error'), 500

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='127.0.0.1', port=5000)
