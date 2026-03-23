import os
from dotenv import load_dotenv
from app import create_app

# Load local .env file
load_dotenv()

# Create app specifically for development
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=app.config.get('DEBUG', True))
