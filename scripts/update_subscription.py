import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up Flask app context
from web_app.app import create_app
from web_app.app.extensions import db
from web_app.app.models import User, Organization

app = create_app('production') # Using production to match docker-compose

with app.app_context():
    # Find the user
    email = 'prog@work.ac.ke'
    user = User.query.filter_by(email=email).first()
    
    if not user:
        print(f"User {email} not found. Creating user and organization...")
        domain = email.split('@')[1]
        org = Organization.query.filter_by(domain=domain).first()
        if not org:
            org = Organization(name='Work AC KE', domain=domain)
            db.session.add(org)
            db.session.flush()
        
        user = User(email=email, organization_id=org.id, role='System Admin')
        user.set_password('NexusPass2026!') # Default password for the new user
        db.session.add(user)
    
    # Update organization plan
    if user.organization:
        user.organization.subscription_plan = 'Industrial Nexus'
        user.organization.name = 'Industrial Nexus Corp' # Giving it a pro name
        db.session.commit()
        print(f"Successfully updated {email}'s organization to Industrial Nexus.")
    else:
        print(f"Error: User {email} has no organization.")
