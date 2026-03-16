from flask import render_template, request, jsonify, session, flash, current_app
from flask_login import login_required, current_user
import requests
from app.extensions import db
from app.models import Transaction
from app.payments import payments_bp

@payments_bp.route('/plans')
def plans():
    """Pricing and plans page - Public"""
    plans_data = [
        {
            'name': 'Starter',
            'price': 29,
            'period': 'month',
            'description': 'Perfect for small operations',
            'features': ['Up to 5 machines', 'Basic predictive maintenance', 'Weekly reports', 'Email support', 'Dashboard access'],
            'highlighted': False,
            'btn_text': 'Choose Plan'
        },
        {
            'name': 'Professional',
            'price': 99,
            'period': 'month',
            'description': 'For growing businesses',
            'features': ['Up to 50 machines', 'Advanced ML analytics', 'Daily reports', 'Priority support', 'API access', 'Custom alerts', 'Data export'],
            'highlighted': True,
            'btn_text': 'Get Started'
        },
        {
            'name': 'Enterprise',
            'price': 299,
            'period': 'month',
            'description': 'For large-scale operations',
            'features': ['Unlimited machines', 'Real-time predictions', 'Hourly reports', '24/7 phone support', 'Advanced API', 'Custom integration', 'Dedicated account manager'],
            'highlighted': False,
            'btn_text': 'Contact Sales'
        }
    ]
    return render_template('plans.html', plans=plans_data)

@payments_bp.route('/checkout/<plan_name>')
@login_required
def checkout(plan_name):
    """Checkout page for payment"""
    plan_mapping = {
        'starter': {'name': 'Starter', 'price': 29, 'plan_id': 'starter_plan'},
        'professional': {'name': 'Professional', 'price': 99, 'plan_id': 'pro_plan'},
        'enterprise': {'name': 'Enterprise', 'price': 299, 'plan_id': 'enterprise_plan'}
    }
    plan = plan_mapping.get(plan_name.lower())
    if not plan:
        return render_template('error.html', message='Invalid plan selected'), 400
    return render_template('checkout.html', plan=plan)

@payments_bp.route('/process', methods=['POST'])
@login_required
def process_payment():
    """Process payment with PayHero"""
    try:
        data = request.json
        plan_name = data.get('plan')
        email = data.get('email') or current_user.email
        phone = data.get('phone')
        
        if not all([plan_name, email, phone]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        plans = {
            'starter': {'amount': 2900, 'currency': 'KES'},
            'professional': {'amount': 9900, 'currency': 'KES'},
            'enterprise': {'amount': 29900, 'currency': 'KES'}
        }
        
        plan_data = plans.get(plan_name.lower())
        if not plan_data:
            return jsonify({'status': 'error', 'message': 'Invalid plan'}), 400
        
        payhero_api_key = current_app.config['PAYHERO_API_KEY']
        api_url = 'https://api.payhero.io/api/v2/payments'
        if current_app.config['PAYHERO_SANDBOX']:
            api_url = 'https://sandbox.payhero.io/api/v2/payments'
        
        payload = {
            'amount': plan_data['amount'],
            'currency': plan_data['currency'],
            'email': email,
            'phone_number': phone,
            'first_name': data.get('first_name', 'Customer'),
            'last_name': data.get('last_name', ''),
            'description': f'IndustriSense AI {plan_name.capitalize()} Plan',
            'callback_url': current_app.config['PAYMENT_SUCCESS_URL'],
            'error_callback_url': current_app.config['PAYMENT_FAIL_URL']
        }
        
        headers = {'Authorization': f'Bearer {payhero_api_key}', 'Content-Type': 'application/json'}
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            result = response.json()
            ref = result.get('id', result.get('reference'))
            
            transaction = Transaction(user_id=current_user.id, reference=ref, amount=plan_data['amount'] / 100, plan_name=plan_name)
            db.session.add(transaction)
            db.session.commit()
            
            session['payment_ref'] = ref
            session['plan'] = plan_name
            session['email'] = email
            
            return jsonify({'status': 'success', 'payment_url': result.get('payment_url', result.get('checkout_url')), 'reference': ref}), 200
        else:
            return jsonify({'status': 'error', 'message': f'Payment gateway error: {response.text}'}), response.status_code
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@payments_bp.route('/success')
@login_required
def payment_success():
    """Payment success callback"""
    payment_ref = request.args.get('reference') or session.get('payment_ref')
    if payment_ref:
        transaction = Transaction.query.filter_by(reference=payment_ref).first()
        if transaction and transaction.status != 'Completed':
            transaction.status = 'Completed'
            current_user.subscription_plan = transaction.plan_name.capitalize()
            db.session.commit()
            flash(f'Plan upgraded to {transaction.plan_name.capitalize()}!', 'success')
    
    plan = session.get('plan', 'Unknown')
    email = session.get('email', current_user.email)
    return render_template('payment_success.html', reference=payment_ref, plan=plan, email=email)

@payments_bp.route('/failure')
def payment_failure():
    error_msg = request.args.get('message', 'Payment was not completed')
    error_code = request.args.get('code', 'Unknown')
    return render_template('payment_failure.html', error_message=error_msg, error_code=error_code)

@payments_bp.route('/verify', methods=['POST'])
@login_required
def verify_payment():
    try:
        data = request.json
        payment_ref = data.get('reference')
        if not payment_ref:
            return jsonify({'status': 'error', 'message': 'No payment reference provided'}), 400
        
        payhero_api_key = current_app.config['PAYHERO_API_KEY']
        api_url = f'https://api.payhero.io/api/v2/payments/{payment_ref}'
        if current_app.config['PAYHERO_SANDBOX']:
            api_url = f'https://sandbox.payhero.io/api/v2/payments/{payment_ref}'
        
        headers = {'Authorization': f'Bearer {payhero_api_key}', 'Content-Type': 'application/json'}
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({'status': 'success', 'payment_status': result.get('status'), 'amount': result.get('amount'), 'email': result.get('email')}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Payment not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
