import os
import logging
from twilio.rest import Client
from django.conf import settings
from decouple import config

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        # Get credentials from settings (which reads from .env)
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_WHATSAPP_FROM
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning("Twilio credentials not fully configured")
        
        try:
            self.client = Client(self.account_sid, self.auth_token)
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            self.client = None
    
    def send_student_credentials(self, phone_number, student_name, student_id, password):
        """
        Send student credentials via WhatsApp
        
        Args:
            phone_number: Parent's phone number with country code
            student_name: Full name of student
            student_id: Student ID card number
            password: Default password (DOB)
        
        Returns:
            dict: Response with success status and message details
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Twilio client not initialized'
            }
        
        try:
            # Clean and format phone number
            phone_number = self._format_phone_number(phone_number)
            
            # Create message body
            message_body = self._create_student_credentials_message(
                student_name, student_id, password
            )
            
            # Send message
            message = self.client.messages.create(
                from_=self.from_number,
                to=phone_number,
                body=message_body
            )
            
            logger.info(f"WhatsApp message sent to {phone_number}. SID: {message.sid}")
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'to': phone_number,
                'from': self.from_number
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to send WhatsApp message: {error_msg}")
            
            # Provide user-friendly error messages
            if 'not a valid phone number' in error_msg.lower():
                user_error = "Invalid phone number format. Please include country code."
            elif 'not a registered whatsapp user' in error_msg.lower():
                user_error = "Phone number is not registered on WhatsApp."
            elif 'sandbox' in error_msg.lower():
                user_error = "Please join the WhatsApp sandbox first by sending the join phrase."
            else:
                user_error = error_msg
            
            return {
                'success': False,
                'error': user_error,
                'raw_error': error_msg
            }
    
    def _format_phone_number(self, phone_number):
        """Format phone number for WhatsApp"""
        # Remove any spaces
        phone_number = phone_number.strip()
        
        # If number doesn't have whatsapp: prefix, add it
        if not phone_number.startswith('whatsapp:'):
            # Ensure number has + prefix for international format
            if not phone_number.startswith('+'):
                # If no +, add +91 for India (adjust as needed)
                if phone_number.startswith('0'):
                    phone_number = '+91' + phone_number[1:]
                elif phone_number.startswith('9') or phone_number.startswith('8') or phone_number.startswith('7'):
                    phone_number = '+91' + phone_number
                else:
                    # Try to add + if not present
                    phone_number = '+' + phone_number
            
            phone_number = f"whatsapp:{phone_number}"
        
        return phone_number
    
    def _create_student_credentials_message(self, student_name, student_id, password):
        """Create the message body for student credentials"""
        return f"""🎓 Welcome {student_name}!

Your student account has been created successfully.

📋 Student ID: {student_id}
🔑 Default Password: {password}

Please login using your Student ID and Password.
For security, please change your password after first login.

Thank you!"""
    
    def send_template_message(self, phone_number, template_sid, template_variables):
        """
        Send a template message (for business-initiated conversations)
        
        Args:
            phone_number: Parent's phone number
            template_sid: Twilio content template SID
            template_variables: Dict of template variables
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Twilio client not initialized'
            }
        
        try:
            phone_number = self._format_phone_number(phone_number)
            
            message = self.client.messages.create(
                from_=self.from_number,
                to=phone_number,
                content_sid=template_sid,
                content_variables=template_variables
            )
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status
            }
            
        except Exception as e:
            logger.error(f"Failed to send template message: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }