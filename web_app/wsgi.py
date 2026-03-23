import os
from app import create_app

# This file is the entry point for production servers (Gunicorn)
app = create_app(os.environ.get('FLASK_ENV', 'production'))
