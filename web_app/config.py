"""Flask Application Configuration"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
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
    PAYHERO_API_KEY = os.environ.get('PAYHERO_API_KEY', '')
    PAYHERO_API_SECRET = os.environ.get('PAYHERO_API_SECRET', '')
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
