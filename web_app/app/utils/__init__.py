from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def plan_required(min_plan):
    """Decorator to restrict access based on subscription plan"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            plans = ['Free', 'Starter', 'Professional', 'Enterprise']
            user_plan_idx = plans.index(current_user.subscription_plan)
            min_plan_idx = plans.index(min_plan)
            
            if user_plan_idx < min_plan_idx:
                flash(f'The {min_plan} plan is required to access this feature.', 'info')
                return redirect(url_for('payments.plans'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
