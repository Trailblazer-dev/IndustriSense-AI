from app import create_app
from app.models import User

app = create_app('development')
with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Plan: {user.subscription_plan}")
