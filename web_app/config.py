"""Flask Application Configuration"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    TALISMAN_FORCE_HTTPS = False
    
    # Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True if os.environ.get('FLASK_ENV') == 'production' else False
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600 # 1 hour
    WTF_CSRF_ENABLED = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'industrisense.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Model paths
    MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'models')
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
    # Maximum tool wear observed in training dataset (minutes)
    MAX_TOOL_WEAR = int(os.environ.get('MAX_TOOL_WEAR', 254))
    # Allowed CORS origins (comma-separated) - if empty, CORS is NOT enabled by default
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '')
    
    # Flask settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # PayHero Payment Configuration
    PAYHERO_USERNAME = os.environ.get('PAYHERO_USERNAME', '')
    PAYHERO_AUTH_TOKEN = os.environ.get('Basic_Auth_Token', '')
    PAYHERO_API_PASSWORD = os.environ.get('PAYHERO_API_PASSWORD', '')
    PAYHERO_CHANNEL_ID = os.environ.get('PAYHERO_CHANNEL_ID', '')
    PAYHERO_SANDBOX = os.environ.get('PAYHERO_SANDBOX', 'true').lower() == 'true'
    PAYMENT_SUCCESS_URL = os.environ.get('PAYMENT_SUCCESS_URL', 'http://localhost:5000/payment/success')
    PAYMENT_FAIL_URL = os.environ.get('PAYMENT_FAIL_URL', 'http://localhost:5000/payment/failure')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    TALISMAN_FORCE_HTTPS = True
    # SECRET_KEY must be set via environment variable in production
    @classmethod
    def validate(cls):
        """Validate production configuration"""
        if not os.environ.get('SECRET_KEY'):
            raise ValueError('SECRET_KEY environment variable not set for production')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
