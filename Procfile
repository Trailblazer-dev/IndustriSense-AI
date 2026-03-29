web: gunicorn web_app.wsgi:app
worker: celery -A web_app.app.tasks:celery worker --loglevel=info
