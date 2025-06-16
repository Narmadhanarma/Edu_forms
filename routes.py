import os
import secrets
from flask import render_template, redirect, url_for, flash, request, jsonify, send_file, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from datetime import datetime
import logging

from app import app, db
from models import Organization, Form, Submission, Backup, AuditLog
from forms import RegistrationForm, LoginForm, FormBuilderForm, DynamicSubmissionForm
from services.email_service import send_welcome_email, send_submission_notification
from services.whatsapp_service import create_whatsapp_group, send_whatsapp_invite
from services.backup_service import create_backup, restore_from_backup, get_backup_list
from services.export_service import export_submissions_to_excel, export_submissions_to_csv
from utils import get_form_templates, create_dynamic_form, log_audit_event

@app.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Organization registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if organization already exists
        org = Organization.query.filter_by(email=form.email.data).first()
        if org:
            flash('Email address already registered.', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Create new organization
        organization = Organization(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            whatsapp_number=form.whatsapp_number.data,
            address=form.address.data,
            organization_type=form.organization_type.data,
            is_verified=True  # Auto-verify for demo purposes
        )
        organization.set_password(form.password.data)
        
        db.session.add(organization)
        db.session.commit()
        
        # Log audit event
        log_audit_event('organization_registered', f'Organization {organization.name} registered', 
                       organization.id, request.remote_addr, request.user_agent.string)
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Organization login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        organization = Organization.query.filter_by(email=form.email.data).first()
        if organization and organization.check_password(form.password.data):
            if not organization.is_verified:
                flash('Your organization is not verified yet. Please contact support.', 'warning')
                return render_template('auth/login.html', form=form)
            
            login_user(organization, remember=form.remember_me.data)
            
            # Log audit event
            log_audit_event('organization_login', f'Organization {organization.name} logged in', 
                           organization.id, request.remote_addr, request.user_agent.string)
            
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('dashboard')
            return redirect(next_page)
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Organization logout"""
    # Log audit event
    log_audit_event('organization_logout', f'Organization {current_user.name} logged out', 
                   current_user.id, request.remote_addr, request.user_agent.string)
    
    logout_user()
    return redirect(url_for('index'))

# Dashboard routes
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    forms = Form.query.filter_by(organization_id=current_user.id).order_by(Form.created_at.desc()).all()
    templates = get_form_templates()
    
    # Get statistics
    total_forms = len(forms)
    total_submissions = sum(form.submission_count for form in forms)
    active_forms = len([form for form in forms if form.is_active])
    
    return render_template('dashboard/dashboard.html', 
                         forms=forms, 
                         templates=templates,
                         total_forms=total_forms,
                         total_submissions=total_submissions,
                         active_forms=active_forms)

@app.route('/form/builder/<template_type>')
@login_required
def form_builder(template_type):
    """Form builder page"""
    templates = get_form_templates()
    if template_type not in templates:
        flash('Invalid template type.', 'danger')
        return redirect(url_for('dashboard'))
    
    template = templates[template_type]
    return render_template('dashboard/form_builder.html', template=template, template_type=template_type)

@app.route('/form/create', methods=['POST'])
@login_required
def create_form():
    """Create a new form"""
    try:
        data = request.get_json()
        
        # Generate unique link
        unique_link = secrets.token_urlsafe(16)
        while Form.query.filter_by(unique_link=unique_link).first():
            unique_link = secrets.token_urlsafe(16)
        
        # Create form
        form = Form(
            title=data['title'],
            description=data.get('description', ''),
            template_type=data['template_type'],
            unique_link=unique_link,
            max_submissions=int(data.get('max_submissions', 40)),
            organization_id=current_user.id
        )
        
        # Set form fields (ensure email and whatsapp are mandatory)
        fields = data.get('fields', [])
        mandatory_fields = [
            {'name': 'name', 'type': 'text', 'label': 'Full Name', 'required': True},
            {'name': 'email', 'type': 'email', 'label': 'Email Address', 'required': True},
            {'name': 'whatsapp_number', 'type': 'tel', 'label': 'WhatsApp Number', 'required': True}
        ]
        
        # Add custom fields after mandatory ones
        all_fields = mandatory_fields + fields
        form.set_form_fields(all_fields)
        
        db.session.add(form)
        db.session.commit()
        
        # Log audit event
        log_audit_event('form_created', f'Form "{form.title}" created', 
                       current_user.id, request.remote_addr, request.user_agent.string)
        
        return jsonify({
            'success': True, 
            'form_url': url_for('submit_form', unique_link=unique_link, _external=True),
            'form_id': form.id
        })
        
    except Exception as e:
        logging.error(f"Error creating form: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create form'}), 500

@app.route('/form/preview/<int:form_id>')
@login_required
def form_preview(form_id):
    """Preview a form"""
    form = Form.query.filter_by(id=form_id, organization_id=current_user.id).first_or_404()
    return render_template('dashboard/form_preview.html', form=form)

@app.route('/form/manage')
@login_required
def form_management():
    """Form management page"""
    forms = Form.query.filter_by(organization_id=current_user.id).order_by(Form.created_at.desc()).all()
    return render_template('dashboard/form_management.html', forms=forms)

@app.route('/form/toggle/<int:form_id>', methods=['POST'])
@login_required
def toggle_form_status(form_id):
    """Toggle form active status"""
    form = Form.query.filter_by(id=form_id, organization_id=current_user.id).first_or_404()
    form.is_active = not form.is_active
    db.session.commit()
    
    status = 'activated' if form.is_active else 'deactivated'
    log_audit_event('form_status_changed', f'Form "{form.title}" {status}', 
                   current_user.id, request.remote_addr, request.user_agent.string)
    
    flash(f'Form {status} successfully.', 'success')
    return redirect(url_for('form_management'))

@app.route('/form/delete/<int:form_id>', methods=['POST'])
@login_required
def delete_form(form_id):
    """Delete a form (with automatic backup)"""
    form = Form.query.filter_by(id=form_id, organization_id=current_user.id).first_or_404()
    
    try:
        # Create automatic backup before deletion
        backup_path = create_backup(form, 'auto')
        
        # Log audit event
        log_audit_event('form_deleted', f'Form "{form.title}" deleted (backup created)', 
                       current_user.id, request.remote_addr, request.user_agent.string)
        
        # Delete form (cascade will handle submissions)
        db.session.delete(form)
        db.session.commit()
        
        flash(f'Form deleted successfully. Backup saved at {backup_path}', 'success')
        
    except Exception as e:
        logging.error(f"Error deleting form: {str(e)}")
        flash('Error deleting form. Please try again.', 'danger')
    
    return redirect(url_for('form_management'))

# Form submission routes
@app.route('/f/<unique_link>')
def submit_form(unique_link):
    """Public form submission page"""
    form = Form.query.filter_by(unique_link=unique_link).first_or_404()
    
    if not form.can_accept_submissions():
        return render_template('forms/form_closed.html', form=form)
    
    # Create dynamic form based on form fields
    submission_form = create_dynamic_form(form.get_form_fields())
    
    return render_template('forms/submit_form.html', form=form, submission_form=submission_form)

@app.route('/f/<unique_link>/submit', methods=['POST'])
def process_form_submission(unique_link):
    """Process form submission"""
    form = Form.query.filter_by(unique_link=unique_link).first_or_404()
    
    if not form.can_accept_submissions():
        flash('This form is no longer accepting submissions.', 'warning')
        return redirect(url_for('submit_form', unique_link=unique_link))
    
    try:
        # Get form data
        form_data = {}
        for field in form.get_form_fields():
            field_name = field['name']
            form_data[field_name] = request.form.get(field_name, '')
        
        # Check for duplicate submissions (optional)
        email = form_data.get('email', '')
        whatsapp = form_data.get('whatsapp_number', '')
        existing = Submission.query.filter_by(
            form_id=form.id, 
            email=email, 
            whatsapp_number=whatsapp
        ).first()
        
        if existing:
            flash('You have already submitted this form.', 'warning')
            return redirect(url_for('submit_form', unique_link=unique_link))
        
        # Create submission
        submission = Submission(
            name=form_data.get('name', ''),
            email=email,
            whatsapp_number=whatsapp,
            form_id=form.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        submission.set_form_data(form_data)
        
        db.session.add(submission)
        
        # Update form submission count
        form.submission_count += 1
        db.session.commit()
        
        # Send welcome email
        try:
            send_welcome_email(email, form_data.get('name', ''), form.title)
        except Exception as e:
            logging.error(f"Error sending welcome email: {str(e)}")
        
        # Add to WhatsApp group
        try:
            if not form.whatsapp_group_link:
                # Create WhatsApp group for this form
                group_link = create_whatsapp_group(form.title, form.organization.whatsapp_number)
                if group_link:
                    form.whatsapp_group_link = group_link
                    db.session.commit()
            
            if form.whatsapp_group_link:
                send_whatsapp_invite(whatsapp, form.whatsapp_group_link)
        except Exception as e:
            logging.error(f"Error with WhatsApp integration: {str(e)}")
        
        return render_template('forms/form_success.html', form=form, submission=submission)
        
    except Exception as e:
        logging.error(f"Error processing form submission: {str(e)}")
        flash('Error submitting form. Please try again.', 'danger')
        return redirect(url_for('submit_form', unique_link=unique_link))

# Export routes
@app.route('/form/<int:form_id>/export/excel')
@login_required
def export_form_excel(form_id):
    """Export form submissions to Excel"""
    form = Form.query.filter_by(id=form_id, organization_id=current_user.id).first_or_404()
    
    try:
        file_path = export_submissions_to_excel(form)
        return send_file(file_path, as_attachment=True, 
                        download_name=f"{form.title}_submissions.xlsx")
    except Exception as e:
        logging.error(f"Error exporting to Excel: {str(e)}")
        flash('Error exporting data. Please try again.', 'danger')
        return redirect(url_for('form_management'))

@app.route('/form/<int:form_id>/export/csv')
@login_required
def export_form_csv(form_id):
    """Export form submissions to CSV"""
    form = Form.query.filter_by(id=form_id, organization_id=current_user.id).first_or_404()
    
    try:
        file_path = export_submissions_to_csv(form)
        return send_file(file_path, as_attachment=True, 
                        download_name=f"{form.title}_submissions.csv")
    except Exception as e:
        logging.error(f"Error exporting to CSV: {str(e)}")
        flash('Error exporting data. Please try again.', 'danger')
        return redirect(url_for('form_management'))

# Backup and restore routes
@app.route('/backups')
@login_required
def backup_management():
    """Backup management page"""
    backups = get_backup_list(current_user.id)
    return render_template('dashboard/backups.html', backups=backups)

@app.route('/backup/create', methods=['POST'])
@login_required
def create_manual_backup():
    """Create manual backup of all forms"""
    try:
        forms = Form.query.filter_by(organization_id=current_user.id).all()
        backup_paths = []
        
        for form in forms:
            backup_path = create_backup(form, 'manual')
            backup_paths.append(backup_path)
        
        flash(f'Manual backup created successfully. {len(backup_paths)} forms backed up.', 'success')
        
    except Exception as e:
        logging.error(f"Error creating manual backup: {str(e)}")
        flash('Error creating backup. Please try again.', 'danger')
    
    return redirect(url_for('backup_management'))

@app.route('/backup/restore/<int:backup_id>', methods=['POST'])
@login_required
def restore_backup(backup_id):
    """Restore from backup"""
    backup = Backup.query.filter_by(id=backup_id, organization_id=current_user.id).first_or_404()
    
    try:
        restored_form = restore_from_backup(backup)
        if restored_form:
            flash(f'Backup restored successfully. Form "{restored_form.title}" has been recreated.', 'success')
        else:
            flash('Error restoring backup. Form may already exist.', 'warning')
            
    except Exception as e:
        logging.error(f"Error restoring backup: {str(e)}")
        flash('Error restoring backup. Please try again.', 'danger')
    
    return redirect(url_for('backup_management'))

@app.route('/backup/download/<int:backup_id>')
@login_required
def download_backup(backup_id):
    """Download backup file"""
    backup = Backup.query.filter_by(id=backup_id, organization_id=current_user.id).first_or_404()
    
    if backup.file_path and os.path.exists(backup.file_path):
        return send_file(backup.file_path, as_attachment=True)
    else:
        flash('Backup file not found.', 'danger')
        return redirect(url_for('backup_management'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403
