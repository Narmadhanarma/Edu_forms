import os
import json
import logging
from datetime import datetime
from app import db
from models import Backup, Form, Submission

def create_backup(form, backup_type='manual'):
    """Create backup of form and its submissions"""
    try:
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join('backups', str(form.organization_id))
        os.makedirs(backup_dir, exist_ok=True)
        
        # Prepare backup data
        backup_data = {
            'form': {
                'title': form.title,
                'description': form.description,
                'template_type': form.template_type,
                'form_fields': form.get_form_fields(),
                'max_submissions': form.max_submissions,
                'created_at': form.created_at.isoformat() if form.created_at else None
            },
            'submissions': []
        }
        
        # Add submissions data
        for submission in form.submissions:
            backup_data['submissions'].append({
                'name': submission.name,
                'email': submission.email,
                'whatsapp_number': submission.whatsapp_number,
                'form_data': submission.get_form_data(),
                'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None,
                'ip_address': submission.ip_address
            })
        
        # Create backup file
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{form.id}_{timestamp}.json"
        file_path = os.path.join(backup_dir, filename)
        
        with open(file_path, 'w') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        # Save backup record to database
        backup_record = Backup(
            backup_type=backup_type,
            file_path=file_path,
            form_title=form.title,
            organization_id=form.organization_id,
            original_form_id=form.id
        )
        backup_record.set_backup_data(backup_data)
        
        db.session.add(backup_record)
        db.session.commit()
        
        logging.info(f"Backup created for form {form.id}: {file_path}")
        return file_path
        
    except Exception as e:
        logging.error(f"Error creating backup for form {form.id}: {str(e)}")
        raise

def restore_from_backup(backup):
    """Restore form from backup"""
    try:
        backup_data = backup.get_backup_data()
        form_data = backup_data.get('form', {})
        
        # Check if form with same title already exists
        existing_form = Form.query.filter_by(
            title=form_data['title'],
            organization_id=backup.organization_id
        ).first()
        
        if existing_form:
            logging.warning(f"Form with title '{form_data['title']}' already exists")
            return None
        
        # Create new form
        import secrets
        unique_link = secrets.token_urlsafe(16)
        while Form.query.filter_by(unique_link=unique_link).first():
            unique_link = secrets.token_urlsafe(16)
        
        restored_form = Form(
            title=form_data['title'] + ' (Restored)',
            description=form_data.get('description', ''),
            template_type=form_data.get('template_type', 'custom'),
            unique_link=unique_link,
            max_submissions=form_data.get('max_submissions', 40),
            organization_id=backup.organization_id
        )
        restored_form.set_form_fields(form_data.get('form_fields', []))
        
        db.session.add(restored_form)
        db.session.flush()  # Get the form ID
        
        # Restore submissions
        submissions_data = backup_data.get('submissions', [])
        for sub_data in submissions_data:
            submission = Submission(
                name=sub_data['name'],
                email=sub_data['email'],
                whatsapp_number=sub_data['whatsapp_number'],
                form_id=restored_form.id
            )
            submission.set_form_data(sub_data.get('form_data', {}))
            db.session.add(submission)
        
        # Update submission count
        restored_form.submission_count = len(submissions_data)
        db.session.commit()
        
        logging.info(f"Form restored from backup {backup.id}: {restored_form.title}")
        return restored_form
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error restoring from backup {backup.id}: {str(e)}")
        raise

def get_backup_list(organization_id):
    """Get list of backups for organization"""
    try:
        backups = Backup.query.filter_by(organization_id=organization_id)\
                             .order_by(Backup.created_at.desc()).all()
        return backups
    except Exception as e:
        logging.error(f"Error getting backup list for org {organization_id}: {str(e)}")
        return []

def cleanup_old_backups(organization_id, days_to_keep=30):
    """Clean up old backup files"""
    try:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        old_backups = Backup.query.filter_by(organization_id=organization_id)\
                                 .filter(Backup.created_at < cutoff_date).all()
        
        for backup in old_backups:
            # Delete file if it exists
            if backup.file_path and os.path.exists(backup.file_path):
                os.remove(backup.file_path)
            
            # Delete database record
            db.session.delete(backup)
        
        db.session.commit()
        logging.info(f"Cleaned up {len(old_backups)} old backups for org {organization_id}")
        
    except Exception as e:
        logging.error(f"Error cleaning up old backups: {str(e)}")
