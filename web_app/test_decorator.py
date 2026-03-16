from app import create_app
from app.models import User
from app.utils import plan_required
from flask import Flask, session
from flask_login import login_user, current_user, LoginManager

app = create_app('development')

@app.route('/test_pro')
@plan_required('Professional')
def test_pro():
    return "Success"

def test_logic():
    with app.test_request_context():
        # Mock a Free user
        user = User.query.filter_by(email='vimrichy@gmail.com').first()
        login_user(user)
        
        print(f"Testing access for user {user.email} with plan {user.subscription_plan}")
        try:
            # We call the function directly to see if the decorator logic hits
            # But decorators return a wrapper, we need to call the wrapper
            resp = test_pro()
            print(f"Response: {resp}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_logic()
