from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import random
import logging

from .models import StudentPass
from .serializers import (
    StudentPassSerializer,
    StudentPassUpdateSerializer,
    StudentPassLoginSerializer,
    RequestForgotPasswordOtpSerializer,
    VerifyOtpAndResetPasswordSerializer,
)
from services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)

# OTP config
OTP_TTL_SECONDS = 300         # 5 minutes
OTP_RESEND_COOLDOWN = 60      # 60 seconds


def _otp_key(card):
    return f"sp_otp:{card}"


def _cooldown_key(card):
    return f"sp_otp_cool:{card}"


# ==================================================
# LIST / DETAIL / UPDATE / DELETE
# ==================================================
class StudentPassListView(APIView):
    def get(self, request):
        student_passes = StudentPass.objects.all()
        serializer = StudentPassSerializer(student_passes, many=True)
        return Response(
            {"success": True, "count": student_passes.count(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class StudentPassDetailView(APIView):
    def get_object(self, pk):
        try:
            return StudentPass.objects.get(pk=pk)
        except StudentPass.DoesNotExist:
            return None

    def get(self, request, pk):
        sp = self.get_object(pk)
        if not sp:
            return Response({"success": False, "message": "Student pass not found"},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "data": StudentPassSerializer(sp).data},
                        status=status.HTTP_200_OK)

    def patch(self, request, pk):
        sp = self.get_object(pk)
        if not sp:
            return Response({"success": False, "message": "Student pass not found"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = StudentPassUpdateSerializer(sp, data=request.data, partial=True)
        if serializer.is_valid():
            updated = serializer.save()
            return Response({
                "success": True,
                "message": "Student pass updated successfully",
                "data": StudentPassSerializer(updated).data
            }, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        sp = self.get_object(pk)
        if not sp:
            return Response({"success": False, "message": "Student pass not found"},
                            status=status.HTTP_404_NOT_FOUND)
        sp.delete()
        return Response({"success": True, "message": "Student pass deleted successfully"},
                        status=status.HTTP_200_OK)


# ==================================================
# LOGIN
# ==================================================
class StudentPassLoginView(APIView):
    def post(self, request):
        serializer = StudentPassLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        card = serializer.validated_data['student_id_card']
        pwd = serializer.validated_data['password']

        try:
            sp = StudentPass.objects.get(student_id_card=card, is_active=True)
        except StudentPass.DoesNotExist:
            return Response({"success": False,
                             "message": "Invalid student ID card or account inactive"},
                            status=status.HTTP_404_NOT_FOUND)

        # check_password() only matches the CURRENT hash.
        # After password reset, old password can never match.
        if not sp.check_password(pwd):
            return Response({"success": False, "message": "Invalid password"},
                            status=status.HTTP_401_UNAUTHORIZED)

        sp.last_login = timezone.now()
        sp.save(update_fields=["last_login", "updated_at"])

        return Response({
            "success": True,
            "message": "Login successful",
            "data": StudentPassSerializer(sp).data
        }, status=status.HTTP_200_OK)


# ==================================================
# STEP 1 — SEND OTP
# ==================================================
class RequestForgotPasswordOtpView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_send"   # 5/hour from settings

    def post(self, request):
        serializer = RequestForgotPasswordOtpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        card = serializer.validated_data['student_id_card']
        dob = serializer.validated_data['dob']

        try:
            sp = StudentPass.objects.get(student_id_card=card, is_active=True)
        except StudentPass.DoesNotExist:
            return Response({"success": False,
                             "message": "Student pass not found or inactive"},
                            status=status.HTTP_404_NOT_FOUND)

        if sp.student.dob != dob:
            return Response({"success": False,
                             "message": "Invalid DOB for this student ID card"},
                            status=status.HTTP_400_BAD_REQUEST)

        phone = sp.student.parent_phone
        if not phone:
            return Response({"success": False,
                             "message": "Parent phone number not available"},
                            status=status.HTTP_400_BAD_REQUEST)

        # resend cooldown
        if cache.get(_cooldown_key(card)):
            return Response({"success": False,
                             "message": "Please wait before requesting another OTP"},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        otp = f"{random.randint(100000, 999999)}"
        cache.set(_otp_key(card), otp, timeout=OTP_TTL_SECONDS)

        name = f"{sp.student.first_name} {sp.student.last_name}"
        result = WhatsAppService().send_otp(
            phone_number=phone,
            otp=otp,
            student_name=name,
            expiry_minutes=OTP_TTL_SECONDS // 60,
        )

        if not result.get("success"):
            cache.delete(_otp_key(card))
            logger.error(f"OTP send failed for {card}: {result}")
            return Response({"success": False,
                             "message": "Could not send OTP. Please try again later.",
                             "error": result.get("error")},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        cache.set(_cooldown_key(card), True, timeout=OTP_RESEND_COOLDOWN)

        payload = {
            "success": True,
            "message": f"OTP sent on WhatsApp to the registered number for {name}",
            "expires_in_seconds": OTP_TTL_SECONDS,
        }
        if settings.DEBUG:
            payload["debug_otp"] = otp   # never leaks in production
        return Response(payload, status=status.HTTP_200_OK)


# ==================================================
# STEP 2 — VERIFY OTP + RESET PASSWORD
# ==================================================
class VerifyOtpAndResetPasswordView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_verify"   # 10/hour

    def post(self, request):
        serializer = VerifyOtpAndResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        card = serializer.validated_data['student_id_card']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        cached_otp = cache.get(_otp_key(card))
        if not cached_otp or cached_otp != otp:
            return Response({"success": False, "message": "Invalid or expired OTP"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            sp = StudentPass.objects.get(student_id_card=card, is_active=True)
        except StudentPass.DoesNotExist:
            return Response({"success": False, "message": "Student pass not found"},
                            status=status.HTTP_404_NOT_FOUND)

        # set_password(new) re-hashes with a NEW salt.
        # Old password will never match again.
        sp.set_password(new_password)
        sp.save()

        # clear OTP + cooldown
        cache.delete(_otp_key(card))
        cache.delete(_cooldown_key(card))

        return Response({
            "success": True,
            "message": "Password updated successfully. Please login with your new password."
        }, status=status.HTTP_200_OK)


# ==================================================
# LOGOUT
# ==================================================
class StudentPassLogoutView(APIView):
    def post(self, request):
        card = request.data.get('student_id_card')
        if not card:
            return Response({"success": False, "message": "student_id_card is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            StudentPass.objects.get(student_id_card=card)
            # agar JWT/Knox use kar rahe ho, token blacklist yahan karein
            return Response({"success": True, "message": "Logged out successfully"},
                            status=status.HTTP_200_OK)
        except StudentPass.DoesNotExist:
            return Response({"success": False, "message": "Student pass not found"},
                            status=status.HTTP_404_NOT_FOUND)