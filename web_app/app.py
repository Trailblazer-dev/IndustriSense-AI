"""IndustriSense AI - Flask Web Application"""
import os
import pickle
import json
import pandas as pd
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from config import config

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Load trained models and data
def load_models():
    """Load trained XGBoost models"""
    model_dir = app.config['MODEL_DIR']
    try:
        with open(os.path.join(model_dir, 'xgboost_classifier.pkl'), 'rb') as f:
            classifier = pickle.load(f)
        with open(os.path.join(model_dir, 'xgboost_wear_regressor.pkl'), 'rb') as f:
            regressor = pickle.load(f)
        return classifier, regressor
    except FileNotFoundError as e:
        print(f"Error loading models: {e}")
        return None, None

def load_data():
    """Load feature-engineered data (SCALED version for model compatibility)"""
    data_dir = app.config['DATA_DIR']
    try:
        # IMPORTANT: Load SCALED features because models were trained on scaled data
        # Using raw features causes extreme predictions (near 100%) due to feature magnitude mismatch
        df = pd.read_csv(os.path.join(data_dir, 'features_engineered_scaled.csv'))
        return df
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        print(f"Note: Trying raw features as fallback (not recommended)...")
        try:
            # Fallback to raw if scaled not available
            df = pd.read_csv(os.path.join(data_dir, 'features_engineered_raw.csv'))
            return df
        except FileNotFoundError:
            return None

# Load models and data at startup
classifier, regressor = load_models()
df = load_data()

# Also load raw features for display purposes (scaled values can't be directly interpreted)
def load_raw_data():
    """Load raw (unscaled) features for display"""
    data_dir = app.config['DATA_DIR']
    try:
        df_raw = pd.read_csv(os.path.join(data_dir, 'features_engineered_raw.csv'))
        return df_raw
    except FileNotFoundError:
        print(f"Warning: Raw features not available for display. Using scaled values.")
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
    'Torque [Nm]', 'Stress Index', 'Temp Diff [K]',
    'Temp_Diff_x_Wear', 'Speed_x_Torque', 'is_anomaly'
]

# ==================== Routes ====================

@app.route('/')
def dashboard():
    """Dashboard - Main page with machine overview (Hybrid: Actual + Predicted)"""
    if df is None:
        return render_template('error.html', message='Data not loaded'), 500
    
    # Sample 10 machines for dashboard
    np.random.seed(42)
    sample_indices = np.random.choice(len(df), 10, replace=False)
    
    machines = []
    for idx in sample_indices:
        # Use scaled data for model predictions
        row_scaled = df.iloc[idx]
        X_classifier = row_scaled[FEATURE_COLS_CLASSIFIER].values.reshape(1, -1)
        X_regressor = row_scaled[FEATURE_COLS_REGRESSOR].values.reshape(1, -1)
        
        # Failure risk prediction
        failure_prob = float(classifier.predict_proba(X_classifier)[0][1]) * 100
        
        # HYBRID: Actual tool wear (ground truth)
        if df_raw is not None:
            row_raw = df_raw.iloc[idx]
            actual_tool_wear = float(row_raw['Tool wear [min]'])
        else:
            actual_tool_wear = float(row_scaled['Tool wear [min]'])
        
        # HYBRID: Predicted tool wear (model estimate)
        predicted_tool_wear = float(regressor.predict(X_regressor)[0])
        
        # HYBRID: RUL values (both actual and predicted)
        actual_rul = max(0, 253 - int(actual_tool_wear))
        predicted_rul = max(0, 253 - int(predicted_tool_wear))
        
        # HYBRID: Prediction error (how far off was the model?)
        wear_error = abs(actual_tool_wear - predicted_tool_wear)
        
        # HYBRID: Model reliability flag (is regressor accurate?)
        model_reliability = "UNRELIABLE" if abs(wear_error) > 50 else "MODERATE" if abs(wear_error) > 20 else "GOOD"
        
        machines.append({
            'id': int(idx),
            'failure_risk': round(failure_prob, 1),
            # Actual values (ground truth)
            'actual_tool_wear': round(actual_tool_wear, 1),
            'actual_rul': actual_rul,
            # Predicted values (model estimates)
            'predicted_tool_wear': round(predicted_tool_wear, 1),
            'predicted_rul': predicted_rul,
            # Model accuracy metric
            'wear_error': round(wear_error, 2),
            'error_percent': round((wear_error / 253) * 100, 1),
            'model_reliability': model_reliability,
            # Status based on actual failure risk
            'status': 'CRITICAL' if failure_prob >= 95 else ('WARNING' if failure_prob >= 50 else 'NORMAL'),
            'timestamp': datetime.now().isoformat()
        })
    
    return render_template('dashboard.html', machines=machines)

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
    if classifier is None or regressor is None:
        return jsonify({'error': 'Models not loaded'}), 500
    
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'features' not in data:
            return jsonify({'error': 'Missing features in request'}), 400
        
        features = data['features']
        
        # Create feature arrays
        X_classifier = np.array([features]).reshape(1, -1)
        X_regressor = np.array([features[:len(FEATURE_COLS_REGRESSOR)]]).reshape(1, -1)
        
        # Make predictions
        failure_prob = float(classifier.predict_proba(X_classifier)[0][1])
        tool_wear = float(regressor.predict(X_regressor)[0])
        rul = max(0, 253 - int(tool_wear))
        
        return jsonify({
            'success': True,
            'failure_probability': round(failure_prob * 100, 2),
            'tool_wear_minutes': round(tool_wear, 2),
            'remaining_useful_life': rul,
            'risk_level': 'CRITICAL' if failure_prob >= 0.7 else ('WARNING' if failure_prob >= 0.4 else 'NORMAL'),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/machines/<int:machine_id>')
def get_machine_details(machine_id):
    """Get details for a specific machine (Hybrid: Actual + Predicted)"""
    if df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    if machine_id < 0 or machine_id >= len(df):
        return jsonify({'error': f'Machine {machine_id} not found'}), 404
    
    # Use scaled data for model predictions
    row_scaled = df.iloc[machine_id]
    X_classifier = row_scaled[FEATURE_COLS_CLASSIFIER].values.reshape(1, -1)
    X_regressor = row_scaled[FEATURE_COLS_REGRESSOR].values.reshape(1, -1)
    
    # Predictions
    failure_prob = float(classifier.predict_proba(X_classifier)[0][1])
    predicted_tool_wear = float(regressor.predict(X_regressor)[0])
    
    # Actual values (ground truth)
    if df_raw is not None:
        row_raw = df_raw.iloc[machine_id]
        actual_tool_wear = float(row_raw['Tool wear [min]'])
    else:
        actual_tool_wear = float(row_scaled['Tool wear [min]'])
    
    # Calculate RUL values
    actual_rul = max(0, 253 - int(actual_tool_wear))
    predicted_rul = max(0, 253 - int(predicted_tool_wear))
    
    # Prediction error
    wear_error = abs(actual_tool_wear - predicted_tool_wear)
    error_percent = (wear_error / 253) * 100
    
    # Model reliability assessment
    model_reliability = "UNRELIABLE" if abs(wear_error) > 50 else "MODERATE" if abs(wear_error) > 20 else "GOOD"
    reliability_warning = {
        "UNRELIABLE": "⚠️ EXPERIMENTAL: RUL predictions have high error margins (>50 min). Use for reference only.",
        "MODERATE": "⚠️ BETA: RUL predictions have moderate error (±20-50 min). Consider actual measured values.",
        "GOOD": "✓ RUL prediction within acceptable range (±<20 min). More reliable for use."
    }
    
    return jsonify({
        'machine_id': machine_id,
        'features': {feat: float(row_scaled[feat]) for feat in FEATURE_COLS_CLASSIFIER},
        'failure_analysis': {
            'probability_percent': round(failure_prob * 100, 2),
            'status': 'CRITICAL' if failure_prob >= 0.95 else ('WARNING' if failure_prob >= 0.5 else 'NORMAL'),
            'note': '✓ Failure classifier is production-ready (83.8% recall)'
        },
        'tool_wear_analysis': {
            'actual_tool_wear_minutes': round(actual_tool_wear, 2),
            'predicted_tool_wear_minutes': round(predicted_tool_wear, 2),
            'prediction_error_minutes': round(wear_error, 2),
            'prediction_error_percent': round(error_percent, 2),
            'max_tool_wear_threshold': 253
        },
        'rul_analysis': {
            'actual_remaining_useful_life': actual_rul,
            'predicted_remaining_useful_life': predicted_rul,
            'rul_difference': abs(actual_rul - predicted_rul)
        },
        'model_reliability': {
            'status': model_reliability,
            'warning': reliability_warning[model_reliability],
            'assessment': 'Failure risk classifier is accurate. RUL regressor is in beta and requires improvement.'
        },
        'model_performance_note': 'TRANSPARENCY REPORT: Actual values show ground truth; Predicted shows model estimate; Error indicates model accuracy gap.',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats')
def get_stats():
    """Get overall system statistics for dashboard sample machines (not entire dataset)"""
    if df is None or classifier is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    # Use SAME sample indices as dashboard (fixed seed for consistency)
    np.random.seed(42)
    sample_indices = np.random.choice(len(df), 10, replace=False)
    
    # Calculate statistics ONLY for sampled machines
    df_sample = df.iloc[sample_indices]
    X_classifier = df_sample[FEATURE_COLS_CLASSIFIER].values
    predictions = classifier.predict_proba(X_classifier)[:, 1]
    
    return jsonify({
        'total_machines': len(df_sample),  # ← 10 machines, not 10,000
        'critical_count': int((predictions >= 0.95).sum()),
        'warning_count': int(((predictions >= 0.5) & (predictions < 0.95)).sum()),
        'normal_count': int((predictions < 0.5).sum()),
        'average_failure_risk': round(float(predictions.mean()) * 100, 2),
        'max_failure_risk': round(float(predictions.max()) * 100, 2),
        'timestamp': datetime.now().isoformat()
    })

# ==================== Error Handlers ====================

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
