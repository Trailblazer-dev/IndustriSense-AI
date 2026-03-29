import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from flask import current_app
import sys

# Ensure src.models is accessible
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.models import model_utils

# Feature columns constants
FEATURE_COLS_CLASSIFIER = [
    'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]',
    'Torque [Nm]', 'Tool wear [min]', 'Stress Index', 'Temp Diff [K]',
    'Temp_Diff_x_Wear', 'Speed_x_Torque', 'is_anomaly'
]

FEATURE_COLS_REGRESSOR = [
    'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]',
    'Torque [Nm]', 'Temp Diff [K]', 'Speed_x_Torque', 'is_anomaly'
]

# Lazy-loaded globals
_models = {'classifier': None, 'regressor': None}
_data = {'raw': None, 'scaled': None}
_scaler = None

def get_scaler():
    """Lazily load the fitted StandardScaler artifact."""
    global _scaler
    if _scaler is not None:
        return _scaler
    
    # Try joblib then legacy pickle
    joblib_path = os.path.join(current_app.config['MODEL_DIR'], 'scaler.joblib')
    pkl_path = os.path.join(current_app.config['MODEL_DIR'], 'scaler.pkl')
    
    target_path = joblib_path if os.path.exists(joblib_path) else pkl_path
    
    try:
        if os.path.exists(target_path):
            _scaler = joblib.load(target_path)
            return _scaler
    except Exception as e:
        print(f"Error loading scaler from {target_path}: {e}")
    return None

def validate_telemetry(raw_data_dict):
    """
    Data Quality Layer: Sanitize sensor telemetry before it hits the AI engine.
    Handles physical constraints, outliers, and noise common in industrial environments.
    """
    try:
        air_temp = float(raw_data_dict.get('air_temp', 0))
        proc_temp = float(raw_data_dict.get('process_temp', 0))
        rpm = float(raw_data_dict.get('rpm', 0))
        torque = float(raw_data_dict.get('torque', 0))
        wear = float(raw_data_dict.get('tool_wear', 0))
        
        # 1. Physical Constraint Validation
        if air_temp < 200 or air_temp > 400:
            return None, "Air temperature outside of industrial operating range (200K - 400K)."
        if proc_temp < 200 or proc_temp > 500:
            return None, "Process temperature outside of industrial operating range (200K - 500K)."
        
        # 2. Outlier/Sensor Noise Detection
        if rpm < 0 or rpm > 5000:
            return None, "Rotational speed outside of valid operating range (0 - 5000 RPM)."
        if torque < 0 or torque > 500:
            return None, "Torque peak outside of valid operating range (0 - 500 Nm)."
        if wear < 0 or wear > 1000:
            return None, "Tool wear value exceeds sensor maximum (1000 min)."
            
        # 3. Cross-Sensor Sanity Check
        if air_temp > proc_temp:
            return None, "Sensor conflict: Ambient temperature exceeds process temperature."
            
        return {
            'air_temp': air_temp,
            'process_temp': proc_temp,
            'rpm': rpm,
            'torque': torque,
            'tool_wear': wear,
            'is_anomaly': int(raw_data_dict.get('is_anomaly', 0))
        }, None
    except (ValueError, TypeError):
        return None, "Telemetry contains non-numeric characters or missing fields."

def generate_work_order(machine_id, status, reason):
    """
    Actionable Feedback Layer: Mock integration with a Maintenance Management System (CMMS).
    Converts a 'Prediction' into a 'Task'.
    """
    order_id = f"WO-{machine_id}-{datetime.now().strftime('%m%d%H%M')}"
    priority = "URGENT" if status == "CRITICAL" else "NORMAL"
    
    return {
        'order_id': order_id,
        'machine_id': machine_id,
        'priority': priority,
        'assigned_to': 'Fleet Maintenance Team A',
        'instruction': f"Perform diagnostics on #{{machine_id}} due to {{reason.lower()}}.",
        'status': 'Draft - Awaiting Approval'
    }

def preprocess_input(raw_data_dict):
    """
    Perform on-the-fly feature engineering and scaling for a single raw input.
    Now includes a Data Quality validation step.
    """
    # Sanitize and Validate Data Quality first
    valid_data, error = validate_telemetry(raw_data_dict)
    if error:
        raise ValueError(error)

    # 1. Feature Engineering (Matches Notebook 2)
    air_temp = valid_data['air_temp']
    proc_temp = valid_data['process_temp']
    rpm = valid_data['rpm']
    torque = valid_data['torque']
    wear = valid_data['tool_wear']
    is_anomaly = valid_data['is_anomaly']

    temp_diff = proc_temp - air_temp
    stress_index = torque * wear
    speed_torque = rpm * torque
    temp_diff_wear = temp_diff * wear

    # Create a full engineered row (in correct order for scaler)
    # Features to scale (matches persist_scaler.py):
    # ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]',
    #  'Torque [Nm]', 'Tool wear [min]', 'Stress Index', 'Temp Diff [K]',
    #  'Temp_Diff_x_Wear', 'Speed_x_Torque']
    
    features_to_scale_values = [
        air_temp, proc_temp, rpm, torque, wear,
        stress_index, temp_diff, temp_diff_wear, speed_torque
    ]
    
    # 2. Scaling
    scaler = get_scaler()
    if scaler:
        # Scaler expects a 2D array [[f1, f2, ...]]
        scaled_values = scaler.transform([features_to_scale_values])[0]
    else:
        # Fallback to unscaled if artifact missing (not ideal)
        print("Warning: Using unscaled features for classifier due to missing scaler artifact.")
        scaled_values = features_to_scale_values

    # 3. Construct DataFrames for inference
    # Classifier needs all 9 scaled features + the unscaled 'is_anomaly' flag
    classifier_input_list = list(scaled_values) + [is_anomaly]
    df_classifier = pd.DataFrame([classifier_input_list], columns=FEATURE_COLS_CLASSIFIER)

    # Regressor needs raw features (7 specific ones)
    # ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]',
    #  'Torque [Nm]', 'Temp Diff [K]', 'Speed_x_Torque', 'is_anomaly']
    regressor_input_list = [
        air_temp, proc_temp, rpm, torque, temp_diff, speed_torque, is_anomaly
    ]
    df_regressor = pd.DataFrame([regressor_input_list], columns=FEATURE_COLS_REGRESSOR)

    return df_classifier, df_regressor

def get_models(force_reload=False):
    """Lazily load models with basic integrity logging."""
    global _models
    if _models['classifier'] is not None and not force_reload:
        return _models['classifier'], _models['regressor']

    model_dir = current_app.config['MODEL_DIR']

    try:
        classifier, clf_sha = model_utils.load_classifier(model_dir)
        regressor, reg_sha = model_utils.load_regressor(model_dir)

        _models['classifier'] = classifier
        _models['regressor'] = regressor
        return classifier, regressor

    except Exception as e:
        print(f"Error loading models: {e}")
        _models['classifier'] = None
        _models['regressor'] = None
        return None, None

def get_data(force_reload=False):
    """Lazily load both raw and scaled features for inference"""
    global _data
    if _data['raw'] is not None and _data['scaled'] is not None and not force_reload:
        return _data

    data_dir = current_app.config['DATA_DIR']
    raw_path = os.path.join(data_dir, 'features_engineered_raw.csv')
    scaled_path = os.path.join(data_dir, 'features_engineered_scaled.csv')
    
    try:
        if os.path.exists(raw_path):
            _data['raw'] = pd.read_csv(raw_path)
        if os.path.exists(scaled_path):
            _data['scaled'] = pd.read_csv(scaled_path)
        return _data
    except Exception as e:
        print(f"Error loading data: {e}")
        return _data

def rul_minutes_to_calendar_time(remaining_minutes, operating_hours_per_day=8):
    """Convert RUL from operating minutes to human-readable calendar time."""
    if remaining_minutes <= 0:
        return {
            'minutes': 0, 'hours': 0, 'days': 0, 'weeks': 0, 'months': 0,
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

def get_user_machines(df, user_id, machine_count=10):
    """
    Simulate multi-tenancy by assigning a random, seeded subset of machines.
    The seed is fixed to user_id so the fleet is consistent for that user.
    """
    num_machines = min(machine_count, len(df))
    
    # Use user_id as seed for consistent randomness per user
    user_df = df.sample(n=num_machines, random_state=user_id).copy()
    user_df['original_index'] = user_df.index
    return user_df

def calculate_statuses(failure_probs, predicted_wear):
    """
    Standardized logic to determine machine status.
    failure_probs: array of probabilities (0.0 to 1.0)
    predicted_wear: array of wear values (minutes)
    """
    # Max observed wear in dataset is ~250
    wear_pct = (predicted_wear / 250.0)
    
    # Unified Risk: The higher of model probability or physical wear
    combined_risk = np.maximum(failure_probs, wear_pct)
    combined_risk_pct = combined_risk * 100
    
    statuses = np.full(len(failure_probs), 'NORMAL', dtype='U10')
    
    # CRITICAL: Combined risk >= 75%
    critical_mask = (combined_risk_pct >= 75)
    # WARNING: Combined risk >= 50%
    warning_mask = (combined_risk_pct >= 50)
    
    # Apply masks (critical takes precedence)
    statuses[warning_mask] = 'WARNING'
    statuses[critical_mask] = 'CRITICAL'
    
    return statuses, combined_risk

def perform_fleet_analysis(user_id):
    """
    Centralized high-performance inference engine for user fleets.
    Returns full stats, sampled dashboard assets, and prioritized critical lists.
    """
    from app.models import User
    user = User.query.get(user_id)
    machine_count = user.organization.machine_count if user and user.organization else 10

    data_dict = get_data()
    df_raw_all = data_dict['raw']
    df_scaled_all = data_dict['scaled']
    
    if df_raw_all is None or df_scaled_all is None:
        return None
        
    df_raw_local = get_user_machines(df_raw_all, user_id, machine_count=machine_count)
    user_indices = df_raw_local['original_index'].values
    df_scaled_local = df_scaled_all.iloc[user_indices]
    
    classifier, regressor = get_models()
    if classifier is None or regressor is None:
        return None

    # Vectorized Inference
    X_clf = df_scaled_local[FEATURE_COLS_CLASSIFIER]
    X_reg = df_raw_local[FEATURE_COLS_REGRESSOR]
    
    probs = classifier.predict_proba(X_clf)[:, 1]
    wear = regressor.predict(X_reg)
    statuses, combined_risk = calculate_statuses(probs, wear)
    
    # 1. Fleet-wide Statistics
    total_fleet = len(user_indices)
    fleet_crit_count = int(np.sum(statuses == 'CRITICAL'))
    fleet_warn_count = int(np.sum(statuses == 'WARNING'))
    fleet_avg_risk = float(np.mean(combined_risk) * 100)
    
    # 2. Return All Fleet Machines
    # Sort by combined risk probability descending
    all_indices = np.arange(len(user_indices))
    sorted_indices = all_indices[np.argsort(combined_risk)][::-1]
    
    max_wear = current_app.config.get('MAX_TOOL_WEAR', 254)
    timestamp = datetime.now().isoformat()
    
    # ... rest of recommendation logic ...
    def get_recommendation(status, risk, tool_wear):
        # Update thresholds to match unified risk logic
        if status == 'CRITICAL':
            reason = 'Critical Risk Threshold Exceeded'
            action = 'IMMEDIATE SHUTDOWN'
        elif status == 'WARNING':
            reason = 'Elevated Risk Level Detected'
            action = 'SCHEDULE INSPECTION'
        else:
            reason = 'Optimal Operation'
            action = 'ROUTINE DUTY'
        return reason, action

    monitored_sample = []
    for l_idx in sorted_indices:
        risk_pct = round(float(combined_risk[l_idx] * 100), 1)
        wear_min = round(float(wear[l_idx]), 1)
        status = statuses[l_idx]
        reason, action = get_recommendation(status, risk_pct, wear_min)
        
        monitored_sample.append({
            'id': int(user_indices[l_idx]),
            'failure_risk': risk_pct,
            'predicted_tool_wear': wear_min,
            'predicted_rul': max(0, max_wear - int(wear[l_idx])),
            'status': status,
            'reason': reason,
            'action': action,
            'timestamp': timestamp
        })
        
    # 3. Sample Statistics
    sample_stats = {
        'total': len(monitored_sample),
        'critical': int(np.sum([1 for m in monitored_sample if m['status'] == 'CRITICAL'])),
        'warning': int(np.sum([1 for m in monitored_sample if m['status'] == 'WARNING'])),
        'normal': int(np.sum([1 for m in monitored_sample if m['status'] == 'NORMAL'])),
        'at_risk': int(np.sum([1 for m in monitored_sample if m['status'] != 'NORMAL'])),
        'avg_risk': round(float(np.mean([m['failure_risk'] for m in monitored_sample])), 1) if monitored_sample else 0,
        'health': round(float(100 - np.mean([m['failure_risk'] for m in monitored_sample])), 1) if monitored_sample else 100
    }

    return {
        'fleet_stats': {
            'total': total_fleet,
            'critical': fleet_crit_count,
            'warning': fleet_warn_count,
            'health': round(100 - fleet_avg_risk, 1)
        },
        'sample_stats': sample_stats,
        'monitored_sample': monitored_sample
    }
