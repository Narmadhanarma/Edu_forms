import os
import logging
from flask_mail import Message
from app import mail

def send_welcome_email(email, name, form_title):
    """Send welcome email to form submitter"""
    try:
        msg = Message(
            subject=f'Thank you for submitting {form_title}',
            recipients=[email],
            html=f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">Hello {name}!</h2>
                <p>Thank you for submitting the <strong>{form_title}</strong> form.</p>
                <p>We have received your submission and will process it accordingly.</p>
                <p>If you have any questions, please don't hesitate to contact us.</p>
                <br>
                <p>Best regards,<br>
                Educational Form System</p>
            </div>
            '''
        )
        mail.send(msg)
        logging.info(f"Welcome email sent to {email}")
        return True
    except Exception as e:
        logging.error(f"Error sending welcome email to {email}: {str(e)}")
        return False

def send_submission_notification(org_email, form_title, submitter_name, submitter_email):
    """Send notification to organization about new submission"""
    try:
        msg = Message(
            subject=f'New submission for {form_title}',
            recipients=[org_email],
            html=f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">New Form Submission</h2>
                <p>You have received a new submission for <strong>{form_title}</strong>.</p>
                <p><strong>Submitter:</strong> {submitter_name} ({submitter_email})</p>
                <p>Please log in to your dashboard to view the complete submission details.</p>
                <br>
                <p>Best regards,<br>
                Educational Form System</p>
            </div>
            '''
        )
        mail.send(msg)
        logging.info(f"Submission notification sent to {org_email}")
        return True
    except Exception as e:
        logging.error(f"Error sending submission notification to {org_email}: {str(e)}")
        return False

def send_backup_notification(org_email, backup_type, form_title):
    """Send backup notification email"""
    try:
        msg = Message(
            subject=f'Backup Created - {form_title}',
            recipients=[org_email],
            html=f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">Backup Created</h2>
                <p>A {backup_type} backup has been created for <strong>{form_title}</strong>.</p>
                <p>You can access and manage your backups from the dashboard.</p>
                <br>
                <p>Best regards,<br>
                Educational Form System</p>
            </div>
            '''
        )
        mail.send(msg)
        logging.info(f"Backup notification sent to {org_email}")
        return True
    except Exception as e:
        logging.error(f"Error sending backup notification to {org_email}: {str(e)}")
        return False
