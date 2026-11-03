import re
import hashlib

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from .models import User
from .serializers import UserSerializer


# =====================================
# TWILIO CLIENT
# =====================================

def get_twilio_client():

    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    service_sid = settings.TWILIO_VERIFY_SERVICE_SID

    if not account_sid or not auth_token or not service_sid:
        raise ValueError("Twilio credentials are not configured.")

    return Client(
        account_sid,
        auth_token
    )


# =====================================
# PHONE NUMBER VALIDATION
# =====================================

def normalize_phone(phone_number):

    phone = str(phone_number).strip()

    # Remove spaces, hyphens and brackets
    phone = re.sub(r'[\s\-()]', '', phone)

    # Indian 10-digit number
    if re.fullmatch(r'[6-9]\d{9}', phone):

        phone = '+91' + phone

    # Indian number with 91 prefix
    elif re.fullmatch(r'91[6-9]\d{9}', phone):

        phone = '+' + phone

    # International E.164 number
    elif re.fullmatch(r'\+[1-9]\d{7,14}', phone):

        pass

    else:

        return None

    return phone


# =====================================
# SEND OTP API
# =====================================

class SendOTPView(APIView):

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp_send'

    def post(self, request):

        phone_number = request.data.get(
            'phone_number', ''
        )

        phone = normalize_phone(phone_number)

        # Phone validation
        if not phone:

            return Response({

                "success": False,

                "message": "Please enter a valid phone number."

            }, status=status.HTTP_400_BAD_REQUEST)

        # Cooldown key
        phone_hash = hashlib.sha256(
            phone.encode()
        ).hexdigest()

        cache_key = f'otp_cooldown_{phone_hash}'

        # Prevent repeated OTP requests
        if not cache.add(
            cache_key,
            True,
            timeout=60
        ):

            return Response({

                "success": False,

                "message": "Please wait 60 seconds before requesting another OTP."

            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:

            client = get_twilio_client()

            verification = (
                client.verify
                .v2
                .services(settings.TWILIO_VERIFY_SERVICE_SID)
                .verifications
                .create(
                    to=phone,
                    channel='sms'
                )
            )

            return Response({

                "success": True,

                "message": "OTP sent successfully.",

                "phone_number": phone,

                "status": verification.status

            }, status=status.HTTP_200_OK)

        except TwilioRestException as e:

            cache.delete(cache_key)

            print("TWILIO ERROR CODE:", e.code)
            print("TWILIO ERROR MESSAGE:", e.msg)
            print("TWILIO ERROR STATUS:", e.status)

            return Response({

                "success": False,

                "message": "Twilio SMS error.",

                "error_code": e.code,

                "error": e.msg

            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:

            cache.delete(cache_key)

            print("OTP SEND ERROR:", str(e))

            return Response({

                "success": False,

                "message": "Something went wrong while sending OTP."

            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =====================================
# VERIFY OTP API
# =====================================

class VerifyOTPView(APIView):

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp_verify'

    def post(self, request):

        phone_number = request.data.get(
            'phone_number', ''
        )

        otp = str(
            request.data.get('otp', '')
        ).strip()

        phone = normalize_phone(phone_number)

        # Validate phone
        if not phone:

            return Response({

                "success": False,

                "message": "Invalid phone number."

            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate OTP
        if not re.fullmatch(r'\d{6}', otp):

            return Response({

                "success": False,

                "message": "Please enter a valid 6-digit OTP."

            }, status=status.HTTP_400_BAD_REQUEST)

        try:

            client = get_twilio_client()

            # Verify OTP using Twilio
            verification_check = (
                client.verify
                .v2
                .services(settings.TWILIO_VERIFY_SERVICE_SID)
                .verification_checks
                .create(
                    to=phone,
                    code=otp
                )
            )

            # OTP not approved
            if verification_check.status != 'approved':

                return Response({

                    "success": False,

                    "message": "Invalid or expired OTP."

                }, status=status.HTTP_400_BAD_REQUEST)

            # =====================================
            # REGISTER OR LOGIN
            # =====================================

            phone_variants = [phone]

            # Support old database numbers
            if phone.startswith('+'):

                phone_variants.append(
                    phone[1:]
                )

            user = User.objects.filter(
                phone_number__in=phone_variants
            ).first()

            if user:

                # Existing user login
                user.phone_number = phone

                user.is_logged_in = True

                user.save()

                action = 'login'

                message = 'Login successful.'

                response_status = status.HTTP_200_OK

            else:

                # New user registration
                user = User.objects.create(

                    phone_number=phone,

                    is_logged_in=True

                )

                action = 'register'

                message = 'Registration successful.'

                response_status = status.HTTP_201_CREATED

            serializer = UserSerializer(user)

            return Response({

                "success": True,

                "message": message,

                "action": action,

                "data": serializer.data

            }, status=response_status)

        except TwilioRestException as e:

            print("TWILIO VERIFY ERROR CODE:", e.code)
            print("TWILIO VERIFY ERROR:", e.msg)

            return Response({

                "success": False,

                "message": "Invalid or expired OTP.",

                "error_code": e.code

            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:

            print("OTP VERIFY ERROR:", str(e))

            return Response({

                "success": False,

                "message": "Something went wrong. Please try again."

            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =====================================
# USER LIST API
# =====================================

class UserListView(APIView):

    def get(self, request):

        users = User.objects.all()

        serializer = UserSerializer(
            users,
            many=True
        )

        return Response({

            "success": True,

            "count": users.count(),

            "data": serializer.data

        }, status=status.HTTP_200_OK)



# =====================================
# USER LOGOUT API
# =====================================

class LogoutView(APIView):

    def post(self, request):

        phone_number = request.data.get("phone_number", "")
        phone = normalize_phone(phone_number)

        if not phone:
            return Response({
                "success": False,
                "message": "Invalid phone number."
            }, status=status.HTTP_400_BAD_REQUEST)

        phone_variants = [phone]

        if phone.startswith("+"):
            phone_variants.append(phone[1:])

        user = User.objects.filter(
            phone_number__in=phone_variants
        ).first()

        if not user:
            return Response({
                "success": False,
                "message": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)

        if not user.is_logged_in:
            return Response({
                "success": True,
                "message": "User is already logged out.",
                "data": {
                    "phone_number": user.phone_number,
                    "is_logged_in": False
                }
            }, status=status.HTTP_200_OK)

        user.is_logged_in = False
        user.save(update_fields=["is_logged_in", "updated_at"])

        return Response({
            "success": True,
            "message": "Logout successful.",
            "data": {
                "phone_number": user.phone_number,
                "is_logged_in": user.is_logged_in
            }
        }, status=status.HTTP_200_OK)

# =====================================
# USER DELETE API
# =====================================

class UserDeleteView(APIView):

    def delete(self, request, user_id):

        user = get_object_or_404(
            User,
            id=user_id
        )

        user.delete()

        return Response({

            "success": True,

            "message": "User deleted successfully."

        }, status=status.HTTP_200_OK)