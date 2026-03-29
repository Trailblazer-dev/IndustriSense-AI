from flask import render_template, redirect, url_for, current_app, request, jsonify, flash
from flask_login import login_required, current_user
import numpy as np
from datetime import datetime, timedelta
import os
import json
import pandas as pd
from app.main import main_bp
from app.utils import plan_required, role_required
from app.services import ml_service as mls
from app.extensions import db
from app.models import ReportArchive

@main_bp.route('/')
def index():
    """Public Landing Page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Fleet Monitor - Focus on a 10-machine sample with consistent stats"""
    analysis = mls.perform_fleet_analysis(current_user.id)
    if not analysis:
        return render_template('error.html', message='Critical failure: Unable to perform fleet inference.'), 500
    
    return render_template('dashboard.html', 
                           machines=analysis['monitored_sample'], 
                           status_counts=analysis['sample_stats'])

@main_bp.route('/reports')
@login_required
@plan_required('Operational Base')
def reports():
    """Operational Audit Report Page matching Dashboard 10-machine view"""
    analysis = mls.perform_fleet_analysis(current_user.id)
    if not analysis:
        return render_template('error.html', message='Critical failure: Report engine offline.'), 500
    
    # Identify non-Normal machines from the monitored 10 for the Action List
    at_risk_machines = [m for m in analysis['monitored_sample'] if m['status'] != 'NORMAL']

    # 1. Financials (Nexus Only)
    financials = None
    if current_user.subscription_plan == 'Industrial Nexus':
        prev_failures = int(analysis['fleet_stats']['critical'] * 0.85)
        savings = prev_failures * 3500
        financials = {
            'prevented': prev_failures, 
            'savings': f"{savings:,}", 
            'roi': round(savings / 1999, 1)
        }

    # 2. Industry Context (Based on user setting or session)
    user_industry = request.args.get('industry') or getattr(current_user, 'industry', 'General Manufacturing')

    # 3. Recent Archives for Sidebar
    recent_archives = ReportArchive.query.filter_by(organization_id=current_user.organization_id)\
        .order_by(ReportArchive.created_at.desc()).limit(5).all()
    
    print(f"DEBUG: Found {len(recent_archives)} recent archives for Org ID {current_user.organization_id}")

    return render_template('reports.html', 
                           stats=analysis['sample_stats'],
                           monitored_assets=analysis['monitored_sample'],
                           at_risk_list=at_risk_machines,
                           report_date=datetime.now().strftime('%B %d, %Y'),
                           financials=financials,
                           industry=user_industry,
                           recent_archives=recent_archives,
                           is_archive=False)

@main_bp.route('/reports/save', methods=['POST'])
@login_required
@plan_required('Production Pro')
@role_required(['Plant Manager', 'System Administrator'])
def save_report():
    """Archive current report state (10 machines) with industry metadata"""
    try:
        analysis = mls.perform_fleet_analysis(current_user.id)
        if not analysis:
            flash('Failed to generate report for archiving.', 'error')
            return redirect(url_for('main.reports'))
            
        summary = analysis['sample_stats']
        at_risk_machines = [m for m in analysis['monitored_sample'] if m['status'] != 'NORMAL']
        
        # Determine Industry from request or user profile
        report_industry = request.form.get('industry') or "General Manufacturing"

        if current_user.subscription_plan == 'Industrial Nexus':
            prev_failures = int(analysis['fleet_stats']['critical'] * 0.85)
            summary['financial_impact'] = {
                'prevented_failures': prev_failures,
                'estimated_savings': prev_failures * 3500,
                'roi': round((prev_failures * 3500) / 1999, 1)
            }
        
        new_report = ReportArchive(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            report_title=f"Audit_{datetime.now().strftime('%Y%m%d_%H%M')}",
            industry=report_industry,
            summary_stats=summary,
            critical_assets=at_risk_machines
        )
        db.session.add(new_report)
        db.session.commit()
        
        flash(f'Operational Audit for {report_industry} successfully archived.', 'success')
        return redirect(url_for('main.reports'))
    except Exception as e:
        print(f"Error saving report: {e}")
        flash('Failed to save report. Please contact system admin.', 'error')
        return redirect(url_for('main.reports'))

@main_bp.route('/reports/archive')
@login_required
@plan_required('Production Pro')
@role_required(['Plant Manager', 'Reliability Engineer', 'System Administrator'])
def reports_archive():
    """Historical Report Browser with Filtering"""
    industry_filter = request.args.get('industry')
    
    query = ReportArchive.query.filter_by(organization_id=current_user.organization_id)
    if industry_filter and industry_filter != 'All':
        query = query.filter_by(industry=industry_filter)
        
    archives = query.order_by(ReportArchive.created_at.desc()).all()
    
    # Get unique industries for filter dropdown
    industries = db.session.query(ReportArchive.industry).filter_by(organization_id=current_user.organization_id).distinct().all()
    industry_list = [i[0] for i in industries if i[0]]
    
    return render_template('reports_archive.html', archives=archives, industries=industry_list, current_filter=industry_filter)

@main_bp.route('/reports/download/<int:report_id>')
@login_required
@plan_required('Production Pro')
@role_required(['Plant Manager', 'Reliability Engineer', 'System Administrator'])
def download_report(report_id):
    """Generate Industry-aware CSV Download"""
    report = ReportArchive.query.get_or_404(report_id)
    if report.organization_id != current_user.organization_id:
        return "Unauthorized", 403
        
    # Create CSV data
    import io
    import csv
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Metadata Header
    writer.writerow(['IndustriSense AI - Audit Report'])
    writer.writerow(['Title', report.report_title])
    writer.writerow(['Industry', report.industry])
    writer.writerow(['Date', report.created_at.strftime('%Y-%m-%d %H:%M')])
    writer.writerow([])
    
    # Summary Section
    writer.writerow(['EXECUTIVE SUMMARY'])
    writer.writerow(['Health Score', f"{report.summary_stats['health']}%"])
    writer.writerow(['Total Monitored', report.summary_stats['total']])
    writer.writerow(['At Risk', report.summary_stats['at_risk']])
    writer.writerow([])
    
    # Assets Section
    writer.writerow(['CRITICAL ASSETS & ACTIONS'])
    writer.writerow(['Machine ID', 'Risk %', 'RUL (min)', 'Reason', 'Required Action'])
    for asset in report.critical_assets:
        writer.writerow([
            asset['id'], 
            asset['failure_risk'], 
            asset['predicted_rul'], 
            asset['reason'], 
            asset['action']
        ])
    
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={report.report_title}_{report.industry}.csv"}
    )

@main_bp.route('/reports/archive/<int:report_id>')
@login_required
@plan_required('Production Pro')
@role_required(['Plant Manager', 'Reliability Engineer', 'System Administrator'])
def view_report_detail(report_id):
    """View a specific archived report in the professional layout"""
    report = ReportArchive.query.get_or_404(report_id)
    if report.organization_id != current_user.organization_id:
        flash('Unauthorized access to report.', 'error')
        return redirect(url_for('main.reports_archive'))
    
    # Format the data to match what reports.html expects
    # Note: Archive only saves critical assets, so monitored_assets will be limited to those
    return render_template('reports.html', 
                           stats=report.summary_stats,
                           monitored_assets=report.critical_assets, # Fallback to critical only for archive
                           at_risk_list=report.critical_assets,
                           report_date=report.created_at.strftime('%B %d, %Y'),
                           financials=report.summary_stats.get('financial_impact'),
                           industry=report.industry,
                           is_archive=True,
                           report_id=report_id)

@main_bp.route('/analytics')
@login_required
@plan_required('Production Pro')
@role_required(['Reliability Engineer', 'System Administrator'])
def analytics():
    """Analytics Page"""
    model_dir = current_app.config['MODEL_DIR']
    importance_data = {'classifier': None, 'regressor': None}
    
    try:
        clf_path = os.path.join(model_dir, 'feature_importance.csv')
        if os.path.exists(clf_path):
            importance_data['classifier'] = pd.read_csv(clf_path).to_dict('records')
        
        reg_path = os.path.join(model_dir, 'wear_feature_importance.csv')
        if os.path.exists(reg_path):
            importance_data['regressor'] = pd.read_csv(reg_path).to_dict('records')
    except Exception as e:
        print(f"Analytics error: {e}")
    
    return render_template('analytics.html', importance_data=importance_data)

@main_bp.route('/predict')
@login_required
@plan_required('Production Pro')
@role_required(['Reliability Engineer', 'System Administrator'])
def predict_interface():
    """Prediction interface"""
    return render_template('predict.html', feature_names=mls.FEATURE_COLS_CLASSIFIER)

@main_bp.route('/models')
@login_required
@role_required(['Reliability Engineer', 'System Administrator'])
def models_page():
    """Technical Specifications"""
    model_dir = current_app.config['MODEL_DIR']
    model_info = {
        'classifier': {'name': 'Failure Classification Model', 'type': 'XGBoost Classifier', 'features': len(mls.FEATURE_COLS_CLASSIFIER), 'classes': 2, 'metrics': None},
        'regressor': {'name': 'Tool Wear RUL Prognosis Model', 'type': 'XGBoost Regressor', 'features': len(mls.FEATURE_COLS_REGRESSOR), 'metrics': None}
    }
    try:
        results_path = os.path.join(model_dir, 'test_results.csv')
        if os.path.exists(results_path):
            model_info['classifier']['metrics'] = pd.read_csv(results_path).to_dict('records')
    except:
        pass
    return render_template('models.html', model_info=model_info)

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')
