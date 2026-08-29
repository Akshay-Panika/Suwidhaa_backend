import os
import logging
from twilio.rest import Client
from django.conf import settings
from dotenv import load_dotenv

# Load .env file
load_dotenv()

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        """
        Initialize WhatsApp service with Twilio credentials
        """
        # Get credentials from settings
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.from_number = getattr(settings, 'TWILIO_WHATSAPP_FROM', '')
        
        # ✅ FIX: If from_number is empty, try environment directly
        if not self.from_number:
            self.from_number = os.getenv("TWILIO_WHATSAPP_FROM") or os.getenv("TWILIO_PHONE_NUMBER", "")
        
        # ✅ FIX: Ensure from_number has whatsapp: prefix
        if self.from_number and not self.from_number.startswith('whatsapp:'):
            # Remove any existing prefix
            if self.from_number.startswith('whatsapp:'):
                self.from_number = self.from_number.replace('whatsapp:', '')
            
            # Clean the number
            self.from_number = self.from_number.strip()
            
            # Ensure + prefix
            if not self.from_number.startswith('+'):
                self.from_number = '+' + self.from_number
            
            # Add whatsapp: prefix
            self.from_number = f"whatsapp:{self.from_number}"
        
        # ✅ Debug - Print initialization status
        print(f"\n{'='*60}")
        print(f"🔍 WHATSAPP SERVICE INITIALIZATION")
        print(f"{'='*60}")
        print(f"📌 Account SID: {self.account_sid[:10] + '...' if self.account_sid else '❌ MISSING'}")
        print(f"📌 Auth Token: {'✅ Present' if self.auth_token else '❌ MISSING'}")
        print(f"📌 From Number: {self.from_number if self.from_number else '❌ MISSING'}")
        print(f"{'='*60}\n")
        
        # ✅ Validate credentials
        if not all([self.account_sid, self.auth_token, self.from_number]):
            missing = []
            if not self.account_sid:
                missing.append("TWILIO_ACCOUNT_SID")
            if not self.auth_token:
                missing.append("TWILIO_AUTH_TOKEN")
            if not self.from_number:
                missing.append("TWILIO_WHATSAPP_FROM or TWILIO_PHONE_NUMBER")
            
            error_msg = f"Missing Twilio credentials: {', '.join(missing)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            self.client = None
            return
        
        # ✅ Initialize Twilio client
        try:
            self.client = Client(self.account_sid, self.auth_token)
            print("✅ Twilio client initialized successfully!")
            logger.info("Twilio client initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize Twilio client: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
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
        # ✅ Check if client is initialized
        if not self.client:
            return {
                'success': False,
                'error': 'Twilio client not initialized. Please check credentials in .env file.',
                'debug': {
                    'account_sid': self.account_sid,
                    'from_number': self.from_number,
                    'auth_token_present': bool(self.auth_token)
                }
            }
        
        try:
            # ✅ Format phone number (adds whatsapp: prefix)
            phone_number = self._format_phone_number(phone_number)
            
            # ✅ Debug logs
            print(f"\n📤 Sending WhatsApp message:")
            print(f"  To: {phone_number}")
            print(f"  From: {self.from_number}")
            
            # ✅ Create message body
            message_body = self._create_student_credentials_message(
                student_name, student_id, password
            )
            
            # ✅ Send message via Twilio
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
            
            # ✅ User-friendly error messages
            if 'not a valid phone number' in error_msg.lower():
                user_error = "Invalid phone number format. Please include country code (e.g., +919898927770)"
            elif 'not a registered whatsapp user' in error_msg.lower():
                user_error = "Phone number is not registered on WhatsApp. Send 'join open-speed' to +14155238886 first."
            elif 'sandbox' in error_msg.lower():
                user_error = "Please join the WhatsApp sandbox first by sending 'join open-speed' to +14155238886"
            elif 'invalid from and to pair' in error_msg.lower():
                user_error = "Invalid From/To pair. Both numbers must have 'whatsapp:' prefix."
            elif 'from' in error_msg.lower() and 'number' in error_msg.lower():
                user_error = f"Invalid From number: {self.from_number}. Check TWILIO_WHATSAPP_FROM in .env file."
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
        
        Args:
            phone_number: Raw phone number
        
        Returns:
            str: Formatted phone number with whatsapp: prefix
        """
        # Remove spaces and special characters (keep + and digits)
        phone_number = ''.join(c for c in phone_number.strip() if c.isdigit() or c == '+')
        
        # If number doesn't have whatsapp: prefix
        if not phone_number.startswith('whatsapp:'):
            # Check if number already has country code
            if not phone_number.startswith('+'):
                # For Indian numbers
                if len(phone_number) == 10:
                    phone_number = '+91' + phone_number
                elif phone_number.startswith('0'):
                    phone_number = '+91' + phone_number[1:]
                elif len(phone_number) == 11 and phone_number.startswith('9'):
                    phone_number = '+91' + phone_number
                else:
                    # Assume it's an Indian number
                    phone_number = '+91' + phone_number
            
            # Add whatsapp: prefix
            phone_number = f"whatsapp:{phone_number}"
        
        return phone_number
    
    def _create_student_credentials_message(self, student_name, student_id, password):
        """
        Create the message body for student credentials
        
        Args:
            student_name: Full name of student
            student_id: Student ID card number
            password: Default password
        
        Returns:
            str: Formatted message
        """
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
        
        Returns:
            dict: Response with success status and message details
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