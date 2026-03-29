from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, limiter
from app.models import User, Organization
from app.auth import auth_bp

# Domain Blacklist: Prevent data leaking across organizations via public providers
PUBLIC_DOMAINS = [
    'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 
    'icloud.com', 'me.com', 'aol.com', 'mail.com', 'protonmail.com'
]

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        company_name = request.form.get('company')
        form_role = request.form.get('role', 'Maintenance Operator')
        
        # 1. Extract domain and check organization
        try:
            domain = email.split('@')[1].lower()
        except (IndexError, AttributeError):
            flash('Invalid email format', 'error')
            return redirect(url_for('auth.register'))

        # Security Check: Prevent public domains from creating organizations
        if domain in PUBLIC_DOMAINS:
            flash(f'The domain {domain} is a public provider. Please use your corporate email address to ensure data security and organization mapping.', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
        
        # 2. Handle Organization logic
        org = Organization.query.filter_by(domain=domain).first()
        is_first_user = False
        
        if not org:
            if not company_name or len(company_name.strip()) < 3:
                flash('Please provide a valid company name to register a new organization.', 'error')
                return redirect(url_for('auth.register'))
            
            # Create new organization for this domain
            org = Organization(name=company_name.strip(), domain=domain)
            db.session.add(org)
            db.session.flush() # Get org.id
            is_first_user = True
        
        # 3. Finalize User creation
        # Auto-promote first user to System Administrator regardless of form choice
        final_role = 'System Administrator' if is_first_user else form_role
        
        user = User(
            email=email, 
            organization_id=org.id, 
            role=final_role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        msg = f'Registration successful! Organization "{org.name}" joined.'
        if is_first_user:
            msg = f'Organization "{org.name}" created. You are the administrator.'
            
        flash(msg, 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per hour")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
