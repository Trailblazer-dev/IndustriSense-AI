from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import os
from celery import Celery

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
talisman = Talisman()

# Initialize Celery with defaults from environment for the worker process
celery = Celery(__name__, 
                broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
                backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))

def init_celery(app):
    """Integrate Celery with Flask context."""
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['RESULT_BACKEND'],
        task_ignore_result=False
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
