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
            self.from_number = self.from_number.replace('whatsapp:', '').strip()
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

    # ---------------- REGISTRATION CREDENTIALS ----------------
    def send_credentials(self, phone_number, name, id_card, password, user_type="Student"):
        if not self.client:
            return {'success': False, 'error': 'Twilio client not initialized'}
        try:
            phone_number = self._format_phone_number(phone_number)
            message_body = self._create_message(name, id_card, password, user_type)
            message = self.client.messages.create(
                from_=self.from_number, to=phone_number, body=message_body
            )
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'to': phone_number,
                'from': self.from_number,
                'user_type': user_type
            }
        except Exception as e:
            error_msg = str(e)
            if 'not a registered whatsapp user' in error_msg.lower() or 'sandbox' in error_msg.lower():
                return {'success': False, 'error': 'Please send "join open-speed" to +14155238886 first'}
            return {'success': False, 'error': error_msg}

    def send_student_credentials(self, phone_number, student_name, student_id, password):
        return self.send_credentials(phone_number, student_name, student_id, password, "Student")

    def send_teacher_credentials(self, phone_number, teacher_name, teacher_id, password):
        return self.send_credentials(phone_number, teacher_name, teacher_id, password, "Teacher")

    # ---------------- CUSTOM MESSAGE ----------------
    def send_custom_message(self, phone_number, message_body):
        if not self.client:
            return {'success': False, 'error': 'Twilio client not initialized'}
        try:
            phone_number = self._format_phone_number(phone_number)
            message = self.client.messages.create(
                from_=self.from_number, to=phone_number, body=message_body
            )
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

    # ---------------- OTP SENDER (WhatsApp) ----------------
    def send_otp(self, phone_number, otp, student_name=None, expiry_minutes=5):
        """Send a one-time password via WhatsApp for forgot-password."""
        if not self.client:
            return {'success': False, 'error': 'Twilio client not initialized'}
        try:
            phone_number = self._format_phone_number(phone_number)
            message_body = self._create_otp_message(
                otp=otp, name=student_name, expiry_minutes=expiry_minutes
            )
            message = self.client.messages.create(
                from_=self.from_number, to=phone_number, body=message_body
            )
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'to': phone_number,
                'from': self.from_number,
            }
        except Exception as e:
            error_msg = str(e)
            if 'not a registered whatsapp user' in error_msg.lower() or 'sandbox' in error_msg.lower():
                return {'success': False, 'error': 'Please send "join open-speed" to +14155238886 first'}
            return {'success': False, 'error': error_msg}

    def _create_otp_message(self, otp, name=None, expiry_minutes=5):
        greeting = f"Hello {name}," if name else "Hello,"
        return f"""🔐 *Password Reset — Suwidhaa*

{greeting}

Your verification code is:

*{otp}*

⏳ This OTP will expire in {expiry_minutes} minutes.
🔒 Never share this code with anyone.

If you did not request this, please ignore this message.

— Suwidhaa Team"""

    def _format_phone_number(self, phone_number):
        phone_number = ''.join(c for c in phone_number.strip() if c.isdigit() or c == '+')
        if phone_number.startswith('whatsapp:'):
            return phone_number
        if phone_number.startswith('0'):
            phone_number = phone_number[1:]
        if not phone_number.startswith('+'):
            if len(phone_number) == 10:
                phone_number = '+91' + phone_number
            elif len(phone_number) == 12 and phone_number.startswith('91'):
                phone_number = '+' + phone_number
            else:
                phone_number = '+91' + phone_number
        return f"whatsapp:{phone_number}"

    def _create_message(self, name, id_card, password, user_type="Student"):
        app_link = "https://play.google.com/store/apps/details?id=com.suwidhaa.app"

        if user_type == "Teacher":
            return f"""🎓 Welcome {name}!

Your teacher account has been created successfully.

📋 Teacher ID: {id_card}
🔑 Default Password: {password}

Please login using your Teacher ID and Password.
For security, please change your password after first login.

📲 Download our app:
{app_link}

Thank you!"""
        else:
            return f"""🎓 Welcome {name}!

Your student account has been created successfully.

📋 Student ID: {id_card}
🔑 Default Password: {password}

Please login using your Student ID and Password.
For security, please change your password after first login.

📲 Download our app:
{app_link}

Thank you!"""