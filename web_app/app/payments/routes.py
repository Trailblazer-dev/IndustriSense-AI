from flask import render_template, request, jsonify, session, flash, current_app
from flask_login import login_required, current_user
import requests
import base64
import time
import os
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
    # Identify current user's plan to highlight it
    current_plan = 'Free'
    if current_user.is_authenticated:
        current_plan = current_user.subscription_plan

    plans_data = [
        {
            'name': 'Operational Base',
            'id': 'essential',
            'price': 20,
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
            'is_current': current_plan == 'Operational Base',
            'btn_text': 'Current Plan' if current_plan == 'Operational Base' else 'Select Base'
        },
        {
            'name': 'Production Pro',
            'id': 'pro',
            'price': 30,
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
            'is_current': current_plan == 'Production Pro',
            'btn_text': 'Current Plan' if current_plan == 'Production Pro' else 'Go Pro'
        },
        {
            'name': 'Industrial Nexus',
            'id': 'enterprise',
            'price': 40,
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
            'is_current': current_plan == 'Industrial Nexus',
            'btn_text': 'Current Plan' if current_plan == 'Industrial Nexus' else 'Contact Sales'
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
        industry = data.get('industry')
        machine_count_raw = data.get('machines')
        
        if not all([plan_name, phone]):
            return jsonify({'status': 'error', 'message': 'Missing fields'}), 400

        # Validate Machine Count (Prevent extreme values)
        try:
            machine_count = int(machine_count_raw)
            if machine_count < 1 or machine_count > 500:
                return jsonify({'status': 'error', 'message': 'Machine count must be between 1 and 500'}), 400
        except (ValueError, TypeError):
            machine_count = 10 # Default fallback
        
        # Local format cleaning (07... or 01...)
        phone_digits = "".join(filter(str.isdigit, phone))
        if phone_digits.startswith('254'):
            phone_digits = phone_digits[3:]
        elif phone_digits.startswith('0'):
            phone_digits = phone_digits[1:]
        
        # Final format: 0XXXXXXXXX
        formatted_phone = '0' + phone_digits

        # PayHero KES testing amounts
        plans = {
            'essential_plan': {'amount': 20, 'name': 'Operational Base'},
            'pro_plan': {'amount': 30, 'name': 'Production Pro'},
            'enterprise_plan': {'amount': 40, 'name': 'Industrial Nexus'}
        }
        
        plan_data = plans.get(plan_name.lower())
        if not plan_data:
            return jsonify({'status': 'error', 'message': 'Invalid plan'}), 400
        
        auth_header = get_payhero_auth()
        if not auth_header:
            return jsonify({'status': 'error', 'message': 'Auth not configured'}), 500

        api_url = 'https://backend.payhero.co.ke/api/v2/payments'
        
        # Priority: Environment Var > Request Root
        callback_url = os.environ.get('CALLBACK_URL')
        if not callback_url:
            base_url = request.url_root.rstrip('/')
            if os.environ.get('FLASK_ENV') == 'production' and 'localhost' not in base_url:
                base_url = base_url.replace('http://', 'https://')
            callback_url = f"{base_url}/payment/callback"
        
        # Get customer name for the payload
        customer_name = f"{current_user.email.split('@')[0]}"
        
        external_ref = f"IND_{current_user.id}_{int(time.time())}"
        payload = {
            'amount': int(plan_data['amount']),
            'phone_number': str(formatted_phone),
            'channel_id': int(current_app.config['PAYHERO_CHANNEL_ID']),
            'provider': "m-pesa",
            'external_reference': str(external_ref),
            'customer_name': str(customer_name),
            'callback_url': str(callback_url)
        }
        
        print(f">>> SENDING TO PAYHERO: {payload}")
        
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        
        print(f"PAYHERO REQUEST: URL={api_url} | Payload={payload}")
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=15)
            print(f"PAYHERO RESPONSE: Status={response.status_code} | Body={response.text}")
        except requests.exceptions.RequestException as req_err:
            print(f"PAYHERO CONNECTION ERROR: {str(req_err)}")
            return jsonify({'status': 'error', 'message': f'Connection failed: {str(req_err)}'}), 500
        
        if response.status_code in [200, 201]:
            res_data = response.json()
            payhero_ref = res_data.get('reference')
            
            transaction = Transaction(
                user_id=current_user.id, 
                reference=external_ref, 
                payhero_reference=payhero_ref,
                amount=plan_data['amount'], 
                plan_name=plan_data['name'],
                industry=industry,
                machine_count=int(machine_count) if machine_count else None
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
        print(f"PAYHERO CALLBACK RECEIVED: {data}")
        if not data: return jsonify({'status': 'error'}), 400
            
        result_code = data.get('ResultCode')
        external_ref = data.get('ExternalReference')
        
        transaction = Transaction.query.filter_by(reference=external_ref).first()
        if not transaction: 
            print(f"CALLBACK ERROR: Transaction {external_ref} not found")
            return jsonify({'status': 'error'}), 404
            
        if str(result_code) == '0' or data.get('Status') in ['Success', 'Completed']:
            transaction.status = 'Completed'
            user = User.query.get(transaction.user_id)
            if user and user.organization: 
                user.organization.subscription_plan = transaction.plan_name
                if transaction.industry:
                    user.organization.industry = transaction.industry
                if transaction.machine_count:
                    user.organization.machine_count = transaction.machine_count
                print(f"CALLBACK SUCCESS: Updated {user.organization.name} to {transaction.plan_name} with {user.organization.machine_count} machines")
            db.session.commit()
        else:
            transaction.status = 'Failed'
            print(f"CALLBACK FAILED: ResultCode {result_code}")
            db.session.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"CALLBACK EXCEPTION: {str(e)}")
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
        print(f"VERIFYING TRANSACTION: {external_ref}")
        
        transaction = Transaction.query.filter_by(reference=external_ref, user_id=current_user.id).first()
        if not transaction: return jsonify({'status': 'error'}), 404

        if transaction.status == 'Completed':
            return jsonify({'status': 'success', 'payment_status': 'Completed'}), 200

        # Proactively check PayHero status as a fallback for missing callbacks
        auth_header = get_payhero_auth()
        # Use PayHero internal GUID if available, otherwise fallback to external reference
        check_ref = transaction.payhero_reference or external_ref
        status_url = f"https://backend.payhero.co.ke/api/v2/transaction-status?reference={check_ref}"
        
        try:
            print(f"POLLING PAYHERO FOR: {check_ref}")
            response = requests.get(status_url, headers={'Authorization': auth_header}, timeout=10)
            print(f"PAYHERO STATUS CHECK: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get('status', '').lower() in ['success', 'completed']:
                    transaction.status = 'Completed'
                    user = User.query.get(transaction.user_id)
                    if user and user.organization: 
                        user.organization.subscription_plan = transaction.plan_name
                        if transaction.industry:
                            user.organization.industry = transaction.industry
                        if transaction.machine_count:
                            user.organization.machine_count = transaction.machine_count
                        print(f"VERIFY SUCCESS: Proactive update for {user.organization.name} to {transaction.plan_name} with {user.organization.machine_count} machines")
                    db.session.commit()
                    return jsonify({'status': 'success', 'payment_status': 'Completed'}), 200
                
                return jsonify({'status': 'success', 'payment_status': res_data.get('status', 'Pending')}), 200
        except Exception as e:
            print(f"VERIFY STATUS API ERROR: {str(e)}")

        return jsonify({'status': 'success', 'payment_status': transaction.status}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
