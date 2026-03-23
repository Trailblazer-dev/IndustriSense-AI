from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    company_name = db.Column(db.String(100))
    industry = db.Column(db.String(100), default='General Manufacturing')
    role = db.Column(db.String(30), default='Maintenance Operator') # Added for RBAC
    subscription_plan = db.Column(db.String(20), default='Free')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    reports = db.relationship('ReportArchive', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='KES')
    status = db.Column(db.String(20), default='Pending') # Pending, Completed, Failed
    plan_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ReportArchive(db.Model):
    __tablename__ = 'report_archives'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_title = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(50)) # Added for industry-specific filtering
    summary_stats = db.Column(db.JSON, nullable=False)
    critical_assets = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
