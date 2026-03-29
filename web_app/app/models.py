from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db

class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    domain = db.Column(db.String(100), unique=True, nullable=False)
    subscription_plan = db.Column(db.String(20), default='Free')
    industry = db.Column(db.String(100), default='General Manufacturing')
    machine_count = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='organization', lazy=True)
    reports = db.relationship('ReportArchive', backref='organization', lazy=True)
    transactions = db.relationship('Transaction', backref='organization', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(30), default='Maintenance Operator')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def subscription_plan(self):
        return self.organization.subscription_plan if self.organization else 'Free'

    @property
    def company_name(self):
        return self.organization.name if self.organization else 'Independent'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    payhero_reference = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='KES')
    status = db.Column(db.String(20), default='Pending') # Pending, Completed, Failed
    plan_name = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    machine_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ReportArchive(db.Model):
    __tablename__ = 'report_archives'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)
    report_title = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(50))
    summary_stats = db.Column(db.JSON, nullable=False)
    critical_assets = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
