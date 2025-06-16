from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class RegistrationForm(FlaskForm):
    """Organization registration form"""
    name = StringField('Organization Name', validators=[DataRequired(), Length(min=2, max=255)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    whatsapp_number = StringField('WhatsApp Number', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    organization_type = SelectField('Organization Type', 
                                  choices=[('school', 'School'),
                                          ('college', 'College'),
                                          ('university', 'University'),
                                          ('institute', 'Institute'),
                                          ('other', 'Other')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    """Organization login form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class FormBuilderForm(FlaskForm):
    """Form for creating/editing forms"""
    title = StringField('Form Title', validators=[DataRequired(), Length(min=2, max=255)])
    description = TextAreaField('Description', validators=[Optional()])
    template_type = SelectField('Template Type', 
                               choices=[('student_admission', 'New Student Admission'),
                                       ('course_enrollment', 'Course Enrollment'),
                                       ('exam_registration', 'Exam Registration'),
                                       ('hostel_accommodation', 'Hostel Accommodation'),
                                       ('scholarship_application', 'Scholarship Application'),
                                       ('internship_placement', 'Internship/Placement Registration'),
                                       ('feedback_complaint', 'Feedback/Complaint'),
                                       ('cultural_program', 'Cultural Program Registration'),
                                       ('college_icm', 'College ICM Registration'),
                                       ('custom', 'Custom Form')])
    max_submissions = StringField('Maximum Submissions', validators=[DataRequired()], default='40')
    submit = SubmitField('Generate Form Link')

class DynamicSubmissionForm(FlaskForm):
    """Base class for dynamic form submissions"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=255)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    whatsapp_number = StringField('WhatsApp Number', validators=[DataRequired(), Length(min=10, max=20)])
    submit = SubmitField('Submit')
