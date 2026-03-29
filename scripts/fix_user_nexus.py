import os
import sys

# Add project root to path
# We are in /app/scripts inside container, so project root is /app
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/web_app')

from flask import Flask
from web_app.app.extensions import db
from web_app.app.models import User, Organization
from web_app.config import config

# Manual app creation to avoid double imports of models
app = Flask(__name__)
app.config.from_object(config['production'])
db.init_app(app)

with app.app_context():
    # Find or create organization
    domain = 'work.ac.ke'
    org = Organization.query.filter_by(domain=domain).first()
    if not org:
        print(f"Creating organization for {domain}...")
        org = Organization(
            name='Industrial Nexus Corp', 
            domain=domain,
            subscription_plan='Industrial Nexus',
            industry='Industrial AI Solutions'
        )
        db.session.add(org)
        db.session.commit()
    else:
        print(f"Updating organization {domain}...")
        org.subscription_plan = 'Industrial Nexus'
        org.name = 'Industrial Nexus Corp'
        db.session.commit()

    # Find or create user
    email = 'prog@work.ac.ke'
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"Creating user {email}...")
        user = User(
            email=email, 
            organization_id=org.id, 
            role='System Admin'
        )
        user.set_password('NexusPass2026!')
        db.session.add(user)
        db.session.commit()
    else:
        print(f"User {email} already exists.")
        user.organization_id = org.id
        db.session.commit()

    print(f"DONE: {email} is now a System Admin for {org.name} with {org.subscription_plan} plan.")
