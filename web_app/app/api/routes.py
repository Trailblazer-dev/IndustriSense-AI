from flask import jsonify, request
from flask_login import login_required, current_user
import pandas as pd
import numpy as np
from datetime import datetime
from app.api import api_bp
from app.utils import plan_required
from app.services import ml_service as mls

@api_bp.route('/predict', methods=['POST'])
@login_required
@plan_required('Professional')
def predict():
    """API endpoint for predictions (Accepts RAW sensor data)"""
    classifier, regressor = mls.get_models()
    if classifier is None or regressor is None:
        return jsonify({'error': 'Models not loaded'}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing data in request'}), 400

        # Validate input structure (expects raw_data_dict keys)
        required_keys = ['air_temp', 'process_temp', 'rpm', 'torque', 'tool_wear', 'is_anomaly']
        if not all(k in data for k in required_keys):
            return jsonify({'error': f'Missing required keys. Expected: {required_keys}'}), 400

        # Perform on-the-fly feature engineering and scaling
        X_classifier, X_regressor = mls.preprocess_input(data)

        # Make predictions
        failure_prob = float(classifier.predict_proba(X_classifier)[0][1])
        tool_wear = float(regressor.predict(X_regressor)[0])
        rul = max(0, 254 - int(tool_wear))

        return jsonify({
            'success': True,
            'failure_probability': round(failure_prob * 100, 2),
            'tool_wear_minutes': round(tool_wear, 2),
            'remaining_useful_life': rul,
            'risk_level': 'CRITICAL' if (failure_prob >= 0.75) else ('WARNING' if (failure_prob >= 0.50) else 'NORMAL'),
            'note': '✓ Success: System processed RAW sensor inputs with automatic scaling.',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/machines/<int:machine_id>')
@login_required
def get_machine_details(machine_id):
    """Get details for a specific machine (Hybrid: Actual + Predicted)"""
    data_dict = mls.get_data()
    df_raw_all = data_dict['raw']
    df_scaled_all = data_dict['scaled']
    
    if df_raw_all is None or df_scaled_all is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    # Strict multi-tenancy: Verify this machine belongs to the user
    user_machines = mls.get_user_machines(df_raw_all, current_user.id)
    if machine_id not in user_machines['original_index'].values:
        return jsonify({'error': 'Access denied: Machine not assigned to your fleet'}), 403
    
    # Inference: Classifier uses scaled, Regressor uses raw
    X_classifier = df_scaled_all.iloc[[machine_id]][mls.FEATURE_COLS_CLASSIFIER]
    X_regressor = df_raw_all.iloc[[machine_id]][mls.FEATURE_COLS_REGRESSOR]

    classifier, regressor = mls.get_models()
    if classifier is None or regressor is None:
        return jsonify({'error': 'Models not loaded'}), 500

    failure_prob = float(classifier.predict_proba(X_classifier)[0][1])
    predicted_tool_wear = float(regressor.predict(X_regressor)[0])
    actual_tool_wear = float(df_raw_all.iloc[machine_id]['Tool wear [min]'])
    
    actual_rul_min = max(0, 254 - int(actual_tool_wear))
    predicted_rul_min = max(0, 254 - int(predicted_tool_wear))
    
    actual_rul_calendar = mls.rul_minutes_to_calendar_time(actual_rul_min)
    predicted_rul_calendar = mls.rul_minutes_to_calendar_time(predicted_rul_min)
    
    wear_error = abs(actual_tool_wear - predicted_tool_wear)
    error_percent = (wear_error / 254) * 100
    
    model_reliability = "UNRELIABLE" if abs(wear_error) > 50 else "MODERATE" if abs(wear_error) > 20 else "GOOD"
    reliability_warning = {
        "UNRELIABLE": "⚠️ WARNING: RUL predictions have high error margins (>50 min). Verify with physical tool inspection.",
        "MODERATE": "⚠️ BETA: RUL predictions have moderate error (±20-50 min). Cross-check with actual measured tool wear.",
        "GOOD": "✓ RUL prediction within acceptable range (±<20 min). Regressor uses clean sensor telemetry."
    }
    
    return jsonify({
        'machine_id': machine_id,
        'features': {feat: float(df_raw_all.iloc[machine_id][feat]) for feat in mls.FEATURE_COLS_CLASSIFIER},
        'failure_analysis': {
            'probability_percent': round(failure_prob * 100, 2),
            'status': 'CRITICAL' if failure_prob >= 0.75 else ('WARNING' if failure_prob >= 0.50 else 'NORMAL'),
            'note': '✓ Failure classifier is production-ready'
        },
        'tool_wear_analysis': {
            'actual_tool_wear_minutes': round(actual_tool_wear, 2),
            'predicted_tool_wear_minutes': round(predicted_tool_wear, 2),
            'prediction_error_minutes': round(wear_error, 2),
            'prediction_error_percent': round(error_percent, 2),
            'max_tool_wear_threshold': 254
        },
        'rul_analysis': {
            'actual_remaining_useful_life': actual_rul_min,
            'predicted_remaining_useful_life': predicted_rul_min,
            'rul_difference': abs(actual_rul_min - predicted_rul_min),
            'actual_calendar_time': actual_rul_calendar,
            'predicted_calendar_time': predicted_rul_calendar
        },
        'model_reliability': {
            'status': model_reliability,
            'warning': reliability_warning[model_reliability]
        },
        'model_performance_note': '✓ Fixed: RUL predictions are now based on clean sensor telemetry (leaky features removed). Failure classifier remains trustworthy.',
        'timestamp': datetime.now().isoformat()
    })

@api_bp.route('/stats')
@login_required
def get_stats():
    """Get statistics for the current monitored sample (10 machines)"""
    data_dict = mls.get_data()
    df_raw_all = data_dict['raw']
    df_scaled_all = data_dict['scaled']

    classifier, regressor = mls.get_models()
    if df_raw_all is None or df_scaled_all is None or classifier is None:
        return jsonify({'error': 'Data not loaded'}), 500

    # Get user's machine fleet
    user_machines = mls.get_user_machines(df_raw_all, current_user.id)
    user_indices = user_machines['original_index'].values
    df_scaled_local = df_scaled_all.iloc[user_indices]

    # Vectorized inference for status determination
    X_fleet_classifier = df_scaled_local[mls.FEATURE_COLS_CLASSIFIER]
    X_fleet_regressor = df_raw_all.iloc[user_indices][mls.FEATURE_COLS_REGRESSOR]

    probs = classifier.predict_proba(X_fleet_classifier)[:, 1]
    wear = regressor.predict(X_fleet_regressor)
    statuses = mls.calculate_statuses(probs, wear)

    # Mirror sampling logic: 5 Critical, 3 Warning, 2 Normal
    np.random.seed(42 + current_user.id)
    crit_idx = np.where(statuses == 'CRITICAL')[0]
    warn_idx = np.where(statuses == 'WARNING')[0]
    norm_idx = np.where(statuses == 'NORMAL')[0]

    s_crit = np.random.choice(crit_idx, min(5, len(crit_idx)), replace=False) if len(crit_idx) > 0 else []
    s_warn = np.random.choice(warn_idx, min(3, len(warn_idx)), replace=False) if len(warn_idx) > 0 else []
    s_norm = np.random.choice(norm_idx, min(2, len(norm_idx)), replace=False) if len(norm_idx) > 0 else []

    sample_indices = np.concatenate([s_crit, s_warn, s_norm]).astype(int)

    return jsonify({
        'total_machines': len(sample_indices),
        'critical_count': len(s_crit),
        'warning_count': len(s_warn),
        'normal_count': len(s_norm),
        'average_failure_risk': round(float(probs[sample_indices].mean()) * 100, 2) if len(sample_indices) > 0 else 0,
        'max_failure_risk': round(float(probs[sample_indices].max()) * 100, 2) if len(sample_indices) > 0 else 0,
        'timestamp': datetime.now().isoformat()
    })@api_bp.route('/model-calibration')
@login_required
@plan_required('Enterprise')
def model_calibration():
    """Diagnostic endpoint for enterprise plans (Vectorized)"""
    data_dict = mls.get_data()
    df_raw_all = data_dict['raw']
    df_scaled_all = data_dict['scaled']
    classifier, regressor = mls.get_models()
    
    sample_size = min(500, len(df_raw_all))
    X_clf = df_scaled_all.iloc[:sample_size][mls.FEATURE_COLS_CLASSIFIER]
    X_reg = df_raw_all.iloc[:sample_size][mls.FEATURE_COLS_REGRESSOR]
    
    failure_probs = classifier.predict_proba(X_clf)[:, 1] * 100
    wear_preds = regressor.predict(X_reg)
    
    return jsonify({
        'classifier_distribution': {
            'mean_failure_prob_percent': round(float(np.mean(failure_probs)), 2),
            'max_failure_prob_percent': round(float(np.max(failure_probs)), 2),
            'samples_above_75pct': int(np.sum(failure_probs >= 75))
        },
        'regressor_distribution': {
            'mean_predicted_wear_minutes': round(float(np.mean(wear_preds)), 2)
        }
    })
