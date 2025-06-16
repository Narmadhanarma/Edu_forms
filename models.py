from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import json

class Organization(UserMixin, db.Model):
    """Organization model for educational institutions"""
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    organization_type = db.Column(db.String(100))  # School, College, University, etc.
    is_verified = db.Column(db.Boolean, default=False)
    whatsapp_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    forms = db.relationship('Form', backref='organization', lazy=True, cascade='all, delete-orphan')
    backups = db.relationship('Backup', backref='organization', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Organization {self.name}>'

class Form(db.Model):
    """Form model for educational forms"""
    __tablename__ = 'forms'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    template_type = db.Column(db.String(100), nullable=False)
    form_fields = db.Column(db.Text, nullable=False)  # JSON string of form fields
    unique_link = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    max_submissions = db.Column(db.Integer, default=40)
    submission_count = db.Column(db.Integer, default=0)
    whatsapp_group_link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    # Relationships
    submissions = db.relationship('Submission', backref='form', lazy=True, cascade='all, delete-orphan')
    
    def get_form_fields(self):
        """Get form fields as Python object"""
        return json.loads(self.form_fields) if self.form_fields else []
    
    def set_form_fields(self, fields):
        """Set form fields from Python object"""
        self.form_fields = json.dumps(fields)
    
    def can_accept_submissions(self):
        """Check if form can accept more submissions"""
        return self.is_active and self.submission_count < self.max_submissions
    
    def __repr__(self):
        return f'<Form {self.title}>'

class Submission(db.Model):
    """Submission model for form responses"""
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    whatsapp_number = db.Column(db.String(20), nullable=False)
    form_data = db.Column(db.Text, nullable=False)  # JSON string of all form data
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)
    
    def get_form_data(self):
        """Get form data as Python object"""
        return json.loads(self.form_data) if self.form_data else {}
    
    def set_form_data(self, data):
        """Set form data from Python object"""
        self.form_data = json.dumps(data)
    
    def __repr__(self):
        return f'<Submission {self.name} - {self.form.title}>'

class Backup(db.Model):
    """Backup model for form and submission backups"""
    __tablename__ = 'backups'
    
    id = db.Column(db.Integer, primary_key=True)
    backup_type = db.Column(db.String(50), nullable=False)  # 'auto', 'manual'
    backup_data = db.Column(db.Text, nullable=False)  # JSON string of backup data
    file_path = db.Column(db.String(500))
    form_title = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    original_form_id = db.Column(db.Integer)  # Can be null if form is deleted
    
    def get_backup_data(self):
        """Get backup data as Python object"""
        return json.loads(self.backup_data) if self.backup_data else {}
    
    def set_backup_data(self, data):
        """Set backup data from Python object"""
        self.backup_data = json.dumps(data)
    
    def __repr__(self):
        return f'<Backup {self.backup_type} - {self.form_title}>'

class AuditLog(db.Model):
    """Audit log for tracking important actions"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    def __repr__(self):
        return f'<AuditLog {self.action}>'
