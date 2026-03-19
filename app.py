import os
import sys

# Ensure the root directory is in the path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import the create_app function from the nested package
# We use the full path to avoid conflict with this file name (app.py)
from web_app.app import create_app

# Create the Flask application instance
# Render's default 'gunicorn app:app' looks for the 'app' variable in 'app.py'
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    # This is used when running locally
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
