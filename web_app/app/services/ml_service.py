import os
import pickle
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
    
    scaler_path = os.path.join(current_app.config['MODEL_DIR'], 'scaler.pkl')
    try:
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                _scaler = pickle.load(f)
            return _scaler
    except Exception as e:
        print(f"Error loading scaler: {e}")
    return None

def preprocess_input(raw_data_dict):
    """
    Perform on-the-fly feature engineering and scaling for a single raw input.
    Expected raw_data_dict keys: 
    ['air_temp', 'process_temp', 'rpm', 'torque', 'tool_wear', 'is_anomaly']
    """
    # 1. Feature Engineering (Matches Notebook 2)
    air_temp = float(raw_data_dict['air_temp'])
    proc_temp = float(raw_data_dict['process_temp'])
    rpm = float(raw_data_dict['rpm'])
    torque = float(raw_data_dict['torque'])
    wear = float(raw_data_dict['tool_wear'])
    is_anomaly = int(raw_data_dict['is_anomaly'])

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

def get_user_machines(df, user_id):
    """Simulate multi-tenancy by assigning a subset of machines to each user."""
    num_machines = 1000
    if len(df) <= num_machines:
        user_df = df.copy()
        user_df['original_index'] = user_df.index
        return user_df
    
    start_idx = (user_id * 100) % (len(df) - num_machines)
    user_df = df.iloc[start_idx : start_idx + num_machines].copy()
    user_df['original_index'] = user_df.index
    return user_df

def calculate_statuses(failure_probs, predicted_wear):
    """
    Standardized logic to determine machine status.
    failure_probs: array of probabilities (0.0 to 1.0)
    predicted_wear: array of wear values (minutes)
    """
    # Convert probabilities to percentage for threshold comparison
    probs_pct = failure_probs * 100
    
    statuses = np.full(len(failure_probs), 'NORMAL', dtype='U10')
    
    # CRITICAL: wear >= 200 OR prob >= 75%
    critical_mask = (predicted_wear >= 200) | (probs_pct >= 75)
    # WARNING: wear >= 150 OR prob >= 50%
    warning_mask = (predicted_wear >= 150) | (probs_pct >= 50)
    
    # Apply masks (critical takes precedence)
    statuses[warning_mask] = 'WARNING'
    statuses[critical_mask] = 'CRITICAL'
    
    return statuses
