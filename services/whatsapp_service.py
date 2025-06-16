import os
import logging
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "whatsapp:+14155238886")

def get_twilio_client():
    """Get Twilio client instance"""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        logging.warning("Twilio credentials not configured")
        return None
    
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def create_whatsapp_group(form_title, admin_number):
    """Create WhatsApp group for form participants"""
    # Note: Twilio doesn't directly support group creation
    # This is a simplified implementation that would need actual WhatsApp Business API
    try:
        client = get_twilio_client()
        if not client:
            return None
        
        # For demo purposes, we'll create a mock group link
        # In production, you would use WhatsApp Business API
        group_link = f"https://chat.whatsapp.com/mock-group-{form_title.replace(' ', '-').lower()}"
        
        logging.info(f"Mock WhatsApp group created: {group_link}")
        return group_link
        
    except Exception as e:
        logging.error(f"Error creating WhatsApp group: {str(e)}")
        return None

def send_whatsapp_invite(phone_number, group_link):
    """Send WhatsApp group invite to participant"""
    try:
        client = get_twilio_client()
        if not client:
            return False
        
        # Ensure phone number is in correct format
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number.lstrip('0')
        
        message_body = f"Hello! You've been invited to join our educational form group. Click here to join: {group_link}"
        
        message = client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            body=message_body,
            to=f'whatsapp:{phone_number}'
        )
        
        logging.info(f"WhatsApp invite sent to {phone_number}, SID: {message.sid}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending WhatsApp invite to {phone_number}: {str(e)}")
        return False

def send_whatsapp_message(phone_number, message_text):
    """Send general WhatsApp message"""
    try:
        client = get_twilio_client()
        if not client:
            return False
        
        # Ensure phone number is in correct format
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number.lstrip('0')
        
        message = client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            body=message_text,
            to=f'whatsapp:{phone_number}'
        )
        
        logging.info(f"WhatsApp message sent to {phone_number}, SID: {message.sid}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending WhatsApp message to {phone_number}: {str(e)}")
        return False

def notify_form_submission(phone_number, form_title, submitter_name):
    """Notify organization admin about new form submission via WhatsApp"""
    try:
        message_text = f"📝 New submission received for '{form_title}' from {submitter_name}. Check your dashboard for details."
        return send_whatsapp_message(phone_number, message_text)
    except Exception as e:
        logging.error(f"Error sending form submission notification: {str(e)}")
        return False
