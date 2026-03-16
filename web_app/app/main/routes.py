from flask import render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
import numpy as np
from datetime import datetime
import os
import pandas as pd
from app.main import main_bp
from app.utils import plan_required
from app.services import ml_service as mls

@main_bp.route('/')
def index():
    """Public Landing Page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Fleet Monitor - User specific overview"""
    data_dict = mls.get_data()
    df_raw_all = data_dict['raw']
    df_scaled_all = data_dict['scaled']
    
    if df_raw_all is None or df_scaled_all is None:
        return render_template('error.html', message='Data not loaded'), 500
    
    df_raw_local = mls.get_user_machines(df_raw_all, current_user.id)
    user_indices = df_raw_local['original_index'].values
    df_scaled_local = df_scaled_all.iloc[user_indices]
    
    classifier, regressor = mls.get_models()
    if classifier is None or regressor is None:
        return render_template('error.html', message='Models not loaded'), 500

    X_all_classifier = df_scaled_local[mls.FEATURE_COLS_CLASSIFIER]
    X_all_regressor = df_raw_local[mls.FEATURE_COLS_REGRESSOR]
    
    all_failure_probs = classifier.predict_proba(X_all_classifier)[:, 1] * 100
    all_predicted_wear = regressor.predict(X_all_regressor)
    
    statuses = np.full(len(df_raw_local), 'NORMAL', dtype='U10')
    warning_mask = (all_predicted_wear >= 150) | (all_failure_probs >= 50)
    critical_mask = (all_predicted_wear >= 200) | (all_failure_probs >= 75)
    
    statuses[warning_mask] = 'WARNING'
    statuses[critical_mask] = 'CRITICAL'
    
    np.random.seed(42 + current_user.id)
    critical_indices = np.where(statuses == 'CRITICAL')[0]
    warning_indices = np.where(statuses == 'WARNING')[0]
    normal_indices = np.where(statuses == 'NORMAL')[0]
    
    sample_critical = np.random.choice(critical_indices, min(5, len(critical_indices)), replace=False) if len(critical_indices) > 0 else []
    sample_warning = np.random.choice(warning_indices, min(3, len(warning_indices)), replace=False) if len(warning_indices) > 0 else []
    sample_normal = np.random.choice(normal_indices, min(2, len(normal_indices)), replace=False) if len(normal_indices) > 0 else []
    
    sample_local_indices = np.concatenate([sample_critical, sample_warning, sample_normal]).astype(int)
    
    machines = []
    max_wear_threshold = current_app.config.get('MAX_TOOL_WEAR', 254)
    
    for local_idx in sample_local_indices:
        original_idx = user_indices[local_idx]
        machines.append({
            'id': int(original_idx),
            'failure_risk': round(all_failure_probs[local_idx], 1),
            'predicted_tool_wear': round(all_predicted_wear[local_idx], 1),
            'predicted_rul': max(0, max_wear_threshold - int(all_predicted_wear[local_idx])),
            'status': statuses[local_idx],
            'timestamp': datetime.now().isoformat()
        })
    
    status_counts = {
        'total': len(machines),
        'critical': sum(1 for m in machines if m['status'] == 'CRITICAL'),
        'warning': sum(1 for m in machines if m['status'] == 'WARNING'),
        'normal': sum(1 for m in machines if m['status'] == 'NORMAL')
    }
    
    return render_template('dashboard.html', machines=machines, status_counts=status_counts)

@main_bp.route('/analytics')
@login_required
@plan_required('Starter')
def analytics():
    """Analytics Page"""
    model_dir = current_app.config['MODEL_DIR']
    importance_data = {'classifier': None, 'regressor': None}
    
    try:
        clf_path = os.path.join(model_dir, 'feature_importance.csv')
        if os.path.exists(clf_path):
            importance_data['classifier'] = pd.read_csv(clf_path).to_dict('records')
        
        reg_path = os.path.join(model_dir, 'wear_feature_importance.csv')
        if os.path.exists(reg_path):
            importance_data['regressor'] = pd.read_csv(reg_path).to_dict('records')
    except Exception as e:
        print(f"Analytics error: {e}")
    
    return render_template('analytics.html', importance_data=importance_data)

@main_bp.route('/predict')
@login_required
@plan_required('Professional')
def predict_interface():
    """Prediction interface"""
    return render_template('predict.html', feature_names=mls.FEATURE_COLS_CLASSIFIER)

@main_bp.route('/models')
def models_page():
    """Technical Specifications"""
    model_dir = current_app.config['MODEL_DIR']
    model_info = {
        'classifier': {'name': 'Failure Classification Model', 'type': 'XGBoost Classifier', 'features': len(mls.FEATURE_COLS_CLASSIFIER), 'classes': 2, 'metrics': None},
        'regressor': {'name': 'Tool Wear RUL Prognosis Model', 'type': 'XGBoost Regressor', 'features': len(mls.FEATURE_COLS_REGRESSOR), 'metrics': None}
    }
    try:
        results_path = os.path.join(model_dir, 'test_results.csv')
        if os.path.exists(results_path):
            model_info['classifier']['metrics'] = pd.read_csv(results_path).to_dict('records')
    except:
        pass
    return render_template('models.html', model_info=model_info)

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')
