import os
import csv
import logging
from datetime import datetime
import pandas as pd
from models import Form, Submission

def export_submissions_to_excel(form):
    """Export form submissions to Excel file"""
    try:
        # Create exports directory if it doesn't exist
        export_dir = os.path.join('exports', str(form.organization_id))
        os.makedirs(export_dir, exist_ok=True)
        
        # Prepare data for export
        data = []
        form_fields = form.get_form_fields()
        
        # Get all submissions
        submissions = Submission.query.filter_by(form_id=form.id).order_by(Submission.submitted_at.desc()).all()
        
        for submission in submissions:
            row = {
                'Submission ID': submission.id,
                'Name': submission.name,
                'Email': submission.email,
                'WhatsApp Number': submission.whatsapp_number,
                'Submitted At': submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if submission.submitted_at else '',
                'IP Address': submission.ip_address or ''
            }
            
            # Add custom form fields
            submission_data = submission.get_form_data()
            for field in form_fields:
                field_name = field.get('name', '')
                field_label = field.get('label', field_name)
                if field_name not in ['name', 'email', 'whatsapp_number']:  # Skip already added fields
                    row[field_label] = submission_data.get(field_name, '')
            
            data.append(row)
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(data)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{form.title.replace(' ', '_')}_{timestamp}.xlsx"
        file_path = os.path.join(export_dir, filename)
        
        # Write to Excel with formatting
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Submissions', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Submissions']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logging.info(f"Excel export created: {file_path}")
        return file_path
        
    except Exception as e:
        logging.error(f"Error exporting to Excel: {str(e)}")
        raise

def export_submissions_to_csv(form):
    """Export form submissions to CSV file"""
    try:
        # Create exports directory if it doesn't exist
        export_dir = os.path.join('exports', str(form.organization_id))
        os.makedirs(export_dir, exist_ok=True)
        
        # Prepare data for export
        form_fields = form.get_form_fields()
        
        # Define CSV headers
        headers = ['Submission ID', 'Name', 'Email', 'WhatsApp Number', 'Submitted At', 'IP Address']
        
        # Add custom form field headers
        for field in form_fields:
            field_name = field.get('name', '')
            field_label = field.get('label', field_name)
            if field_name not in ['name', 'email', 'whatsapp_number']:  # Skip already added fields
                headers.append(field_label)
        
        # Create CSV file
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{form.title.replace(' ', '_')}_{timestamp}.csv"
        file_path = os.path.join(export_dir, filename)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            # Get all submissions
            submissions = Submission.query.filter_by(form_id=form.id).order_by(Submission.submitted_at.desc()).all()
            
            for submission in submissions:
                row = [
                    submission.id,
                    submission.name,
                    submission.email,
                    submission.whatsapp_number,
                    submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if submission.submitted_at else '',
                    submission.ip_address or ''
                ]
                
                # Add custom form field values
                submission_data = submission.get_form_data()
                for field in form_fields:
                    field_name = field.get('name', '')
                    if field_name not in ['name', 'email', 'whatsapp_number']:  # Skip already added fields
                        row.append(submission_data.get(field_name, ''))
                
                writer.writerow(row)
        
        logging.info(f"CSV export created: {file_path}")
        return file_path
        
    except Exception as e:
        logging.error(f"Error exporting to CSV: {str(e)}")
        raise

def export_form_analytics(form):
    """Export form analytics and statistics"""
    try:
        # Create exports directory if it doesn't exist
        export_dir = os.path.join('exports', str(form.organization_id))
        os.makedirs(export_dir, exist_ok=True)
        
        analytics_data = {
            'Form Information': {
                'Title': form.title,
                'Description': form.description,
                'Template Type': form.template_type,
                'Created At': form.created_at.strftime('%Y-%m-%d %H:%M:%S') if form.created_at else '',
                'Max Submissions': form.max_submissions,
                'Current Submissions': form.submission_count,
                'Is Active': form.is_active,
                'Form Link': form.unique_link
            },
            'Submission Statistics': {
                'Total Submissions': form.submission_count,
                'Remaining Slots': form.max_submissions - form.submission_count,
                'Fill Rate': f"{(form.submission_count / form.max_submissions * 100):.1f}%" if form.max_submissions > 0 else "0%"
            }
        }
        
        # Add daily submission stats
        submissions = Submission.query.filter_by(form_id=form.id).all()
        daily_stats = {}
        for submission in submissions:
            if submission.submitted_at:
                date_key = submission.submitted_at.strftime('%Y-%m-%d')
                daily_stats[date_key] = daily_stats.get(date_key, 0) + 1
        
        analytics_data['Daily Submissions'] = daily_stats
        
        # Export to JSON
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{form.title.replace(' ', '_')}_analytics_{timestamp}.json"
        file_path = os.path.join(export_dir, filename)
        
        import json
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analytics_data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Analytics export created: {file_path}")
        return file_path
        
    except Exception as e:
        logging.error(f"Error exporting analytics: {str(e)}")
        raise
