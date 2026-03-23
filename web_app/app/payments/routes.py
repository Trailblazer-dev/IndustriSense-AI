from flask import render_template, request, jsonify, session, flash, current_app
from flask_login import login_required, current_user
import requests
import base64
import time
from app.extensions import db, csrf
from app.models import Transaction, User
from app.payments import payments_bp

def get_payhero_auth():
    """
    Construct the Basic Auth header value based on available configuration.
    Prioritizes Basic_Auth_Token if correctly formatted, falls back to Username:Password.
    """
    token = current_app.config.get('PAYHERO_AUTH_TOKEN')
    username = current_app.config.get('PAYHERO_USERNAME')
    password = current_app.config.get('PAYHERO_API_PASSWORD')
    
    if token and token.strip():
        if token.strip().startswith('Basic '):
            return token.strip()
        return f"Basic {token.strip()}"
    
    if username and password:
        auth_str = f"{username.strip()}:{password.strip()}"
        encoded = base64.b64encode(auth_str.encode()).decode()
        return f"Basic {encoded}"
    
    return None

@payments_bp.route('/plans')
def plans():
    """Industrial ROI Optimized Pricing"""
    plans_data = [
        {
            'name': 'Operational Base',
            'id': 'essential',
            'price': 299,
            'period': 'month',
            'description': 'Core failure detection for specialized production lines.',
            'features': [
                'Monitoring for up to 10 machines',
                'Real-time Critical Failure Alerts',
                'Basic XAI (Explainable AI) Reports',
                'Standard Email Support',
                'Digital Health Dashboard'
            ],
            'highlighted': False,
            'btn_text': 'Select Base'
        },
        {
            'name': 'Production Pro',
            'id': 'pro',
            'price': 999,
            'period': 'month',
            'description': 'Advanced prognosis to eliminate unplanned downtime.',
            'features': [
                'Fleet monitoring (up to 50 machines)',
                'RUL (Remaining Useful Life) Forecasting',
                'Predictive Maintenance Scheduling',
                'High-Priority SMS/Phone Alerts',
                'Quarterly ROI Impact Analysis',
                'API Data Integration'
            ],
            'highlighted': True,
            'btn_text': 'Go Pro'
        },
        {
            'name': 'Industrial Nexus',
            'id': 'enterprise',
            'price': 1999,
            'period': 'month',
            'description': 'Enterprise-wide autonomous equipment intelligence.',
            'features': [
                'Unlimited Machine Integration',
                'Custom ML Model Fine-Tuning',
                'Full SCADA/PLC Bi-directional Sync',
                '24/7/365 On-Call IoT Engineer',
                'On-site Implementation & Training',
                'White-label Executive Reporting'
            ],
            'highlighted': False,
            'btn_text': 'Contact Sales'
        }
    ]
    return render_template('plans.html', plans=plans_data)

@payments_bp.route('/checkout/<plan_name>')
@login_required
def checkout(plan_name):
    """Mapped to Industrial Tiers"""
    plan_mapping = {
        'essential': {'name': 'Operational Base', 'price': 299, 'plan_id': 'essential_plan'},
        'pro': {'name': 'Production Pro', 'price': 999, 'plan_id': 'pro_plan'},
        'enterprise': {'name': 'Industrial Nexus', 'price': 1999, 'plan_id': 'enterprise_plan'}
    }
    plan = plan_mapping.get(plan_name.lower())
    if not plan:
        return render_template('error.html', message='Invalid plan selected'), 400
    return render_template('checkout.html', plan=plan)

@payments_bp.route('/process', methods=['POST'])
@login_required
def process_payment():
    """Processing with Industrial Value amounts"""
    try:
        data = request.json
        plan_name = data.get('plan')
        phone = data.get('phone')
        
        if not all([plan_name, phone]):
            return jsonify({'status': 'error', 'message': 'Missing fields'}), 400
        
        formatted_phone = phone.replace('+254', '0').replace('254', '0')
        if formatted_phone.startswith('7') or formatted_phone.startswith('1'):
            formatted_phone = '0' + formatted_phone

        # PayHero KES Conversion (Approx $1 = 100 KES for STK testing)
        plans = {
            'essential_plan': {'amount': 29900, 'name': 'Operational Base'},
            'pro_plan': {'amount': 99900, 'name': 'Production Pro'},
            'enterprise_plan': {'amount': 199900, 'name': 'Industrial Nexus'}
        }
        
        plan_data = plans.get(plan_name.lower())
        if not plan_data:
            return jsonify({'status': 'error', 'message': 'Invalid plan'}), 400
        
        auth_header = get_payhero_auth()
        if not auth_header:
            return jsonify({'status': 'error', 'message': 'Auth not configured'}), 500

        api_url = 'https://backend.payhero.co.ke/api/v2/payments'
        base_url = request.url_root.rstrip('/')
        callback_url = f"{base_url}/payment/callback"
        
        external_ref = f"IND_{current_user.id}_{int(time.time())}"
        payload = {
            'amount': plan_data['amount'],
            'phone_number': formatted_phone,
            'channel_id': current_app.config['PAYHERO_CHANNEL_ID'],
            'provider': "m-pesa",
            'external_reference': external_ref,
            'callback_url': callback_url,
        }
        
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        
        if response.status_code in [200, 201]:
            transaction = Transaction(
                user_id=current_user.id, 
                reference=external_ref, 
                amount=plan_data['amount'], 
                plan_name=plan_data['name']
            )
            db.session.add(transaction)
            db.session.commit()
            
            session['payment_ref'] = external_ref
            
            return jsonify({
                'status': 'success', 
                'message': 'Industrial license prompt sent to your phone.',
                'reference': external_ref
            }), 200
        else:
            return jsonify({'status': 'error', 'message': f'Provider Error: {response.text}'}), response.status_code
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@payments_bp.route('/callback', methods=['POST'])
@csrf.exempt
def payment_callback():
    try:
        data = request.json
        if not data: return jsonify({'status': 'error'}), 400
            
        result_code = data.get('ResultCode')
        external_ref = data.get('ExternalReference')
        
        transaction = Transaction.query.filter_by(reference=external_ref).first()
        if not transaction: return jsonify({'status': 'error'}), 404
            
        if str(result_code) == '0':
            transaction.status = 'Completed'
            user = User.query.get(transaction.user_id)
            if user: user.subscription_plan = transaction.plan_name
            db.session.commit()
        else:
            transaction.status = 'Failed'
            db.session.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@payments_bp.route('/success')
@login_required
def payment_success():
    payment_ref = request.args.get('reference') or session.get('payment_ref')
    if not payment_ref: return render_template('error.html', message='Reference missing'), 400
        
    transaction = Transaction.query.filter_by(reference=payment_ref, user_id=current_user.id).first()
    if not transaction: return render_template('error.html', message='Unauthorized'), 403
        
    return render_template('payment_success.html', 
                           reference=transaction.reference,
                           plan=transaction.plan_name,
                           email=current_user.email)

@payments_bp.route('/failure')
def payment_failure():
    return render_template('payment_failure.html')

@payments_bp.route('/verify', methods=['POST'])
@login_required
def verify_payment():
    try:
        data = request.json
        external_ref = data.get('reference')
        transaction = Transaction.query.filter_by(reference=external_ref, user_id=current_user.id).first()
        if not transaction: return jsonify({'status': 'error'}), 404

        if transaction.status == 'Completed':
            return jsonify({'status': 'success', 'payment_status': 'Completed'}), 200

        auth_header = get_payhero_auth()
        status_url = f"https://backend.payhero.co.ke/api/v2/transaction-status?reference={external_ref}"
        response = requests.get(status_url, headers={'Authorization': auth_header}, timeout=10)
        
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('status', '').lower() == 'success':
                transaction.status = 'Completed'
                user = User.query.get(transaction.user_id)
                if user: user.subscription_plan = transaction.plan_name
                db.session.commit()
                return jsonify({'status': 'success', 'payment_status': 'Completed'}), 200
            return jsonify({'status': 'success', 'payment_status': res_data.get('status')}), 200
        return jsonify({'status': 'error'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
