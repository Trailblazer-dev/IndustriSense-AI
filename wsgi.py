import os
import sys

# Add the web_app directory to the Python path so the 'app' package can be found
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_app'))

from app import create_app

# Create the Flask application instance
# Render and Gunicorn will look for this 'app' object
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    # This is used when running locally
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
