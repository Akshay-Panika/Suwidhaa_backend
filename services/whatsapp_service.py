import os
import logging
from twilio.rest import Client
from django.conf import settings
from dotenv import load_dotenv  # ✅ Changed from decouple

# Load .env file
load_dotenv()

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        # Get credentials from settings
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_WHATSAPP_FROM
        
        # Debug - Check if loaded
        print(f"\n{'='*50}")
        print(f"WhatsApp Service Initialization")
        print(f"{'='*50}")
        print(f"Account SID: {self.account_sid[:10] + '...' if self.account_sid else '❌ MISSING'}")
        print(f"Auth Token: {'✅ Present' if self.auth_token else '❌ MISSING'}")
        print(f"From Number: {self.from_number if self.from_number else '❌ MISSING'}")
        print(f"{'='*50}\n")
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            missing = []
            if not self.account_sid: missing.append("TWILIO_ACCOUNT_SID")
            if not self.auth_token: missing.append("TWILIO_AUTH_TOKEN")
            if not self.from_number: missing.append("TWILIO_WHATSAPP_FROM")
            logger.error(f"Missing Twilio credentials: {', '.join(missing)}")
            self.client = None
            return
        
        try:
            self.client = Client(self.account_sid, self.auth_token)
            print("✅ Twilio client initialized successfully")
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
                'error': 'Twilio client not initialized. Check credentials.'
            }
        
        try:
            # Format phone number
            phone_number = self._format_phone_number(phone_number)
            
            print(f"\n📤 Sending WhatsApp message:")
            print(f"  To: {phone_number}")
            print(f"  From: {self.from_number}")
            
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
                user_error = "Invalid phone number format. Please include country code (e.g., +919898927770)"
            elif 'not a registered whatsapp user' in error_msg.lower():
                user_error = "Phone number is not registered on WhatsApp. Send join phrase to sandbox first."
            elif 'sandbox' in error_msg.lower():
                user_error = "Please join the WhatsApp sandbox first by sending 'join open-speed' to +14155238886"
            elif 'from' in error_msg.lower() and 'number' in error_msg.lower():
                user_error = "Invalid From number. Check TWILIO_WHATSAPP_FROM in .env file."
            else:
                user_error = error_msg
            
            return {
                'success': False,
                'error': user_error,
                'raw_error': error_msg
            }
    
    def _format_phone_number(self, phone_number):
        """
        Format phone number for WhatsApp
        Since all numbers are Indian, automatically add +91
        """
        # Remove spaces and special characters (keep + and digits)
        phone_number = ''.join(c for c in phone_number.strip() if c.isdigit() or c == '+')
        
        # If number doesn't have whatsapp: prefix
        if not phone_number.startswith('whatsapp:'):
            # Check if number already has country code
            if not phone_number.startswith('+'):
                # For Indian numbers (10 digits or starting with 0)
                if len(phone_number) == 10:
                    phone_number = '+91' + phone_number
                elif phone_number.startswith('0'):
                    phone_number = '+91' + phone_number[1:]
                elif len(phone_number) == 11 and phone_number.startswith('9'):
                    # Sometimes 11 digits starting with 9
                    phone_number = '+91' + phone_number
                else:
                    # Assume it's an Indian number
                    phone_number = '+91' + phone_number
            
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