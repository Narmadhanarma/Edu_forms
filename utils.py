import logging
from datetime import datetime
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
from app import db
from models import AuditLog

def get_form_templates():
    """Get predefined form templates"""
    templates = {
        'student_admission': {
            'title': 'New Student Admission',
            'description': 'Application form for new student admission',
            'icon': 'user-plus',
            'default_fields': [
                {'name': 'student_id', 'type': 'text', 'label': 'Student ID', 'required': False},
                {'name': 'date_of_birth', 'type': 'date', 'label': 'Date of Birth', 'required': True},
                {'name': 'address', 'type': 'textarea', 'label': 'Address', 'required': True},
                {'name': 'parent_name', 'type': 'text', 'label': "Parent's Name", 'required': True},
                {'name': 'parent_phone', 'type': 'tel', 'label': "Parent's Phone", 'required': True},
                {'name': 'previous_school', 'type': 'text', 'label': 'Previous School', 'required': False},
                {'name': 'grade_applying', 'type': 'select', 'label': 'Grade Applying For', 'required': True,
                 'options': ['Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5']}
            ]
        },
        'course_enrollment': {
            'title': 'Course Enrollment',
            'description': 'Registration form for course enrollment',
            'icon': 'book-open',
            'default_fields': [
                {'name': 'course_code', 'type': 'text', 'label': 'Course Code', 'required': True},
                {'name': 'course_name', 'type': 'text', 'label': 'Course Name', 'required': True},
                {'name': 'semester', 'type': 'select', 'label': 'Semester', 'required': True,
                 'options': ['Spring 2024', 'Summer 2024', 'Fall 2024', 'Winter 2025']},
                {'name': 'year_of_study', 'type': 'select', 'label': 'Year of Study', 'required': True,
                 'options': ['1st Year', '2nd Year', '3rd Year', '4th Year']},
                {'name': 'prerequisites_completed', 'type': 'checkbox', 'label': 'Prerequisites Completed', 'required': False}
            ]
        },
        'exam_registration': {
            'title': 'Exam Registration',
            'description': 'Registration form for examinations',
            'icon': 'file-text',
            'default_fields': [
                {'name': 'exam_type', 'type': 'select', 'label': 'Exam Type', 'required': True,
                 'options': ['Midterm', 'Final', 'Entrance', 'Certification']},
                {'name': 'subject', 'type': 'text', 'label': 'Subject', 'required': True},
                {'name': 'exam_date_preference', 'type': 'date', 'label': 'Preferred Exam Date', 'required': False},
                {'name': 'special_requirements', 'type': 'textarea', 'label': 'Special Requirements', 'required': False},
                {'name': 'accommodation_needed', 'type': 'checkbox', 'label': 'Accommodation Needed', 'required': False}
            ]
        },
        'hostel_accommodation': {
            'title': 'Hostel Accommodation',
            'description': 'Application for hostel accommodation',
            'icon': 'home',
            'default_fields': [
                {'name': 'room_preference', 'type': 'select', 'label': 'Room Preference', 'required': True,
                 'options': ['Single', 'Double', 'Triple', 'Any Available']},
                {'name': 'duration', 'type': 'select', 'label': 'Duration', 'required': True,
                 'options': ['1 Semester', '1 Academic Year', '2 Academic Years']},
                {'name': 'dietary_requirements', 'type': 'textarea', 'label': 'Dietary Requirements', 'required': False},
                {'name': 'emergency_contact', 'type': 'text', 'label': 'Emergency Contact', 'required': True},
                {'name': 'emergency_phone', 'type': 'tel', 'label': 'Emergency Phone', 'required': True}
            ]
        },
        'scholarship_application': {
            'title': 'Scholarship Application',
            'description': 'Application form for scholarships',
            'icon': 'award',
            'default_fields': [
                {'name': 'scholarship_type', 'type': 'select', 'label': 'Scholarship Type', 'required': True,
                 'options': ['Merit-based', 'Need-based', 'Sports', 'Research', 'Minority']},
                {'name': 'gpa', 'type': 'number', 'label': 'Current GPA', 'required': True},
                {'name': 'family_income', 'type': 'number', 'label': 'Annual Family Income', 'required': False},
                {'name': 'essay', 'type': 'textarea', 'label': 'Personal Essay (500 words)', 'required': True},
                {'name': 'extracurricular', 'type': 'textarea', 'label': 'Extracurricular Activities', 'required': False}
            ]
        },
        'internship_placement': {
            'title': 'Internship/Placement Registration',
            'description': 'Registration for internship and placement opportunities',
            'icon': 'briefcase',
            'default_fields': [
                {'name': 'program_type', 'type': 'select', 'label': 'Program Type', 'required': True,
                 'options': ['Internship', 'Co-op', 'Full-time Placement']},
                {'name': 'preferred_industry', 'type': 'select', 'label': 'Preferred Industry', 'required': True,
                 'options': ['Technology', 'Finance', 'Healthcare', 'Education', 'Manufacturing', 'Other']},
                {'name': 'skills', 'type': 'textarea', 'label': 'Key Skills', 'required': True},
                {'name': 'resume_link', 'type': 'url', 'label': 'Resume Link', 'required': False},
                {'name': 'availability', 'type': 'text', 'label': 'Availability', 'required': True}
            ]
        },
        'feedback_complaint': {
            'title': 'Feedback/Complaint',
            'description': 'Submit feedback or file a complaint',
            'icon': 'message-square',
            'default_fields': [
                {'name': 'category', 'type': 'select', 'label': 'Category', 'required': True,
                 'options': ['Academic', 'Administrative', 'Facilities', 'Food Services', 'Technology', 'Other']},
                {'name': 'type', 'type': 'select', 'label': 'Type', 'required': True,
                 'options': ['Feedback', 'Complaint', 'Suggestion', 'Compliment']},
                {'name': 'subject', 'type': 'text', 'label': 'Subject', 'required': True},
                {'name': 'description', 'type': 'textarea', 'label': 'Detailed Description', 'required': True},
                {'name': 'priority', 'type': 'select', 'label': 'Priority', 'required': False,
                 'options': ['Low', 'Medium', 'High', 'Urgent']}
            ]
        },
        'cultural_program': {
            'title': 'Cultural Program Registration',
            'description': 'Registration for cultural programs and events',
            'icon': 'music',
            'default_fields': [
                {'name': 'event_name', 'type': 'text', 'label': 'Event Name', 'required': True},
                {'name': 'participation_type', 'type': 'select', 'label': 'Participation Type', 'required': True,
                 'options': ['Solo', 'Group', 'Team']},
                {'name': 'category', 'type': 'select', 'label': 'Category', 'required': True,
                 'options': ['Dance', 'Music', 'Drama', 'Art', 'Literature', 'Sports']},
                {'name': 'experience_level', 'type': 'select', 'label': 'Experience Level', 'required': True,
                 'options': ['Beginner', 'Intermediate', 'Advanced', 'Professional']},
                {'name': 'special_requirements', 'type': 'textarea', 'label': 'Special Requirements', 'required': False}
            ]
        },
        'college_icm': {
            'title': 'College ICM Registration',
            'description': 'Registration for Inter-College Meet',
            'icon': 'users',
            'default_fields': [
                {'name': 'sport_event', 'type': 'select', 'label': 'Sport/Event', 'required': True,
                 'options': ['Basketball', 'Football', 'Cricket', 'Tennis', 'Swimming', 'Track & Field', 'Volleyball']},
                {'name': 'team_individual', 'type': 'select', 'label': 'Team/Individual', 'required': True,
                 'options': ['Team', 'Individual']},
                {'name': 'position', 'type': 'text', 'label': 'Position/Role', 'required': False},
                {'name': 'previous_experience', 'type': 'textarea', 'label': 'Previous Experience', 'required': False},
                {'name': 'medical_conditions', 'type': 'textarea', 'label': 'Any Medical Conditions', 'required': False}
            ]
        },
        'custom': {
            'title': 'Custom Form',
            'description': 'Create a custom form with your own fields',
            'icon': 'edit',
            'default_fields': []
        }
    }
    return templates

def create_dynamic_form(form_fields):
    """Create a dynamic Flask-WTF form based on field definitions"""
    class DynamicForm(FlaskForm):
        pass
    
    for field in form_fields:
        field_name = field.get('name', '')
        field_type = field.get('type', 'text')
        field_label = field.get('label', field_name.title())
        field_required = field.get('required', False)
        
        validators = []
        if field_required:
            validators.append(DataRequired())
        
        # Create appropriate field based on type
        if field_type == 'email':
            validators.append(Email())
            form_field = StringField(field_label, validators=validators)
        elif field_type == 'textarea':
            form_field = TextAreaField(field_label, validators=validators)
        elif field_type == 'number':
            form_field = IntegerField(field_label, validators=validators)
        elif field_type == 'select':
            choices = [(opt, opt) for opt in field.get('options', [])]
            form_field = SelectField(field_label, choices=choices, validators=validators)
        elif field_type == 'checkbox':
            form_field = BooleanField(field_label)
        else:  # Default to text field
            form_field = StringField(field_label, validators=validators)
        
        setattr(DynamicForm, field_name, form_field)
    
    # Add submit button
    setattr(DynamicForm, 'submit', SubmitField('Submit'))
    
    return DynamicForm()

def log_audit_event(action, details, organization_id=None, ip_address=None, user_agent=None):
    """Log audit event"""
    try:
        audit_log = AuditLog(
            action=action,
            details=details,
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(audit_log)
        db.session.commit()
        logging.info(f"Audit log created: {action} - {details}")
    except Exception as e:
        logging.error(f"Error creating audit log: {str(e)}")

def validate_phone_number(phone):
    """Validate phone number format"""
    import re
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10-15 digits)
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False
    
    return True

def format_phone_number(phone):
    """Format phone number for international use"""
    import re
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Add + if not present
    if not digits_only.startswith('+'):
        # Assume it's a US number if 10 digits, otherwise add +
        if len(digits_only) == 10:
            digits_only = '+1' + digits_only
        else:
            digits_only = '+' + digits_only
    
    return digits_only

def generate_form_share_text(form):
    """Generate sharing text for forms"""
    return f"""
🎓 {form.title}

{form.description}

Fill out this form: {request.url_root}f/{form.unique_link}

📝 Quick submission - only takes a few minutes!
✅ Secure and confidential
📧 Instant confirmation email

Organized by: {form.organization.name}
    """.strip()

def calculate_form_analytics(form):
    """Calculate form analytics and statistics"""
    analytics = {
        'total_submissions': form.submission_count,
        'remaining_slots': max(0, form.max_submissions - form.submission_count),
        'fill_rate': (form.submission_count / form.max_submissions * 100) if form.max_submissions > 0 else 0,
        'is_full': form.submission_count >= form.max_submissions,
        'days_active': (datetime.utcnow() - form.created_at).days if form.created_at else 0
    }
    
    # Calculate daily submission rate
    if analytics['days_active'] > 0:
        analytics['daily_submission_rate'] = form.submission_count / analytics['days_active']
    else:
        analytics['daily_submission_rate'] = 0
    
    return analytics
