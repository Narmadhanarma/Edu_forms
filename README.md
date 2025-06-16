<<<<<<< HEAD
# Edu_forms
=======
# Educational Form Generator

A comprehensive web-based platform for educational institutions to create, manage, and distribute custom forms with automated email and WhatsApp integration.

## 🎓 Features

### 🔐 Organization Authentication
- Secure registration and login system for educational organizations
- Organization-scoped access control
- Session management with auto-logout

### 📋 Form Templates & Builder
- **10 Pre-built Templates:**
  - New Student Admission
  - Course Enrollment
  - Exam Registration
  - Hostel Accommodation
  - Scholarship Application
  - Internship/Placement Registration
  - Feedback/Complaint
  - Cultural Program Registration
  - College ICM Registration
  - Custom Form (build from scratch)

### 🎨 Dynamic Form Builder
- Drag-and-drop form field management
- Real-time form preview
- Custom field types: text, textarea, number, date, select, checkbox, etc.
- Mandatory fields: Name, Email, WhatsApp Number
- Field validation and requirements

### 📧 Automated Communications
- **Email Integration:**
  - Welcome emails to form submitters
  - Confirmation notifications
  - Custom email templates
  
- **WhatsApp Integration:**
  - Automatic group creation per form
  - Participant invitations via Twilio API
  - Admin group management

### 💾 Backup & Restore System
- **Automatic Backups:**
  - Created automatically when forms are deleted
  - Includes form configuration and all submissions
  
- **Manual Backups:**
  - On-demand backup creation
  - Download backup files
  
- **One-click Restore:**
  - Restore deleted forms from backups
  - Conflict prevention for existing forms

### 📊 Export & Analytics
- Export submissions to Excel (.xlsx)
- Export submissions to CSV
- Form analytics and statistics
- Submission tracking and management

### 🎯 Form Management
- Unique shareable form links
- Submission limits (up to 40+ per form)
- Form activation/deactivation
- Real-time submission tracking
- Duplicate submission prevention

## 🛠️ Technology Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **SQLite/PostgreSQL** - Database
- **Flask-Login** - Authentication
- **Flask-Mail** - Email functionality
- **Flask-WTF** - Form handling
- **Twilio API** - WhatsApp integration
- **Pandas** - Data export

### Frontend
- **Jinja2** - Template engine
- **Bootstrap 5** - UI framework
- **Font Awesome** - Icons
- **Vanilla JavaScript** - Client-side functionality

### Security
- Password hashing with Werkzeug
- CSRF protection
- Session security
- Input validation and sanitization

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Environment Variables
Create a `.env` file in the root directory:

```bash
# Database
DATABASE_URL=sqlite:///edu_forms.db
# For PostgreSQL: postgresql://user:password@localhost/dbname

# Security
SESSION_SECRET=your-secret-key-here

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Twilio (for WhatsApp)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886

# Optional: Backup settings
BACKUP_RETENTION_DAYS=30
AUTO_BACKUP_ENABLED=true
>>>>>>> c27de92 (Set up the project, add core features, and implement organization login)
