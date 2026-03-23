from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def plan_required(min_plan):
    """Decorator to restrict access based on industrial subscription tier"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # Updated to match new professional industrial tiers
            plans = ['Free', 'Operational Base', 'Production Pro', 'Industrial Nexus']
            
            try:
                user_plan_idx = plans.index(current_user.subscription_plan)
                min_plan_idx = plans.index(min_plan)
            except ValueError:
                # Fallback if user has an old plan name in their session/DB
                user_plan_idx = 0
                min_plan_idx = plans.index(min_plan)
            
            if user_plan_idx < min_plan_idx:
                flash(f'The {min_plan} license is required to access this feature.', 'info')
                return redirect(url_for('payments.plans'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def role_required(roles):
    """Decorator to restrict access based on professional role (RBAC)"""
    if isinstance(roles, str):
        roles = [roles]
        
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                flash(f'Access Denied: Your current role ({current_user.role}) does not have the required authority.', 'error')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
