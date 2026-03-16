import os
from flask import Flask
from config import config
from app.extensions import db, login_manager, csrf, limiter, talisman
from app.models import User

def create_app(config_name='default'):
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Validate production config
    if config_name == 'production':
        config['production'].validate()

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Talisman CSP Configuration
    csp = {
        'default-src': '\'self\'',
        'script-src': ['\'self\'', 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com', '\'unsafe-inline\''],
        'style-src': ['\'self\'', 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com', 'https://fonts.googleapis.com', '\'unsafe-inline\''],
        'font-src': ['\'self\'', 'https://cdnjs.cloudflare.com', 'https://fonts.gstatic.com', 'data:'],
        'img-src': ['\'self\'', 'data:', 'https://images.unsplash.com'],
        'connect-src': ['\'self\'', 'https://cdn.jsdelivr.net']
    }
    talisman.init_app(app, content_security_policy=csp, 
                      force_https=app.config.get('TALISMAN_FORCE_HTTPS', False))
    
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.main import main_bp
    app.register_blueprint(main_bp)

    from app.api import api_bp
    app.register_blueprint(api_bp)

    from app.payments import payments_bp
    app.register_blueprint(payments_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
