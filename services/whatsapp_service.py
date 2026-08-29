import os
import logging
from twilio.rest import Client
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '') or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '') or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = getattr(settings, 'TWILIO_WHATSAPP_FROM', '') or os.getenv("TWILIO_WHATSAPP_FROM") or os.getenv("TWILIO_PHONE_NUMBER", "")
        
        if self.from_number and not self.from_number.startswith('whatsapp:'):
            if self.from_number.startswith('whatsapp:'):
                self.from_number = self.from_number.replace('whatsapp:', '')
            self.from_number = self.from_number.strip()
            if not self.from_number.startswith('+'):
                self.from_number = '+' + self.from_number
            self.from_number = f"whatsapp:{self.from_number}"
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.error("Missing Twilio credentials")
            self.client = None
            return
        
        try:
            self.client = Client(self.account_sid, self.auth_token)
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            self.client = None

    def send_student_credentials(self, phone_number, student_name, student_id, password):
        if not self.client:
            return {'success': False, 'error': 'Twilio client not initialized'}
        
        try:
            phone_number = self._format_phone_number(phone_number)
            message_body = self._create_message(student_name, student_id, password)
            message = self.client.messages.create(from_=self.from_number, to=phone_number, body=message_body)
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'to': phone_number,
                'from': self.from_number
            }
        except Exception as e:
            error_msg = str(e)
            if 'not a registered whatsapp user' in error_msg.lower() or 'sandbox' in error_msg.lower():
                return {'success': False, 'error': 'Please send "join open-speed" to +14155238886 first'}
            return {'success': False, 'error': error_msg}

    def _format_phone_number(self, phone_number):
        phone_number = ''.join(c for c in phone_number.strip() if c.isdigit() or c == '+')
        if not phone_number.startswith('whatsapp:'):
            if not phone_number.startswith('+'):
                phone_number = '+91' + phone_number if len(phone_number) == 10 or phone_number.startswith('0') else '+91' + phone_number
            phone_number = f"whatsapp:{phone_number}"
        return phone_number

    def _create_message(self, student_name, student_id, password):
        return f"""🎓 Welcome {student_name}!

Your student account has been created successfully.

📋 Student ID: {student_id}
🔑 Default Password: {password}

Please login using your Student ID and Password.
For security, please change your password after first login.

Thank you!"""