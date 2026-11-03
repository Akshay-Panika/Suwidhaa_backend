from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from django.core.cache import cache
from django.utils import timezone
import random
import logging

from .models import TeacherPass
from .serializers import (
    TeacherPassSerializer,
    TeacherPassUpdateSerializer,
    TeacherPassLoginSerializer,
    TeacherRequestForgotPasswordOtpSerializer,
    TeacherVerifyOtpAndResetPasswordSerializer,
)
from services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)

OTP_TTL_SECONDS = 300        # 5 minutes
OTP_RESEND_COOLDOWN = 60     # 60 seconds


def _otp_key(card):
    # "tp_" prefix so teacher OTPs never collide with student OTPs
    return f"tp_otp:{card}"


def _cooldown_key(card):
    return f"tp_otp_cool:{card}"


def _get_teacher_phone(teacher):
    """Return teacher's phone from whichever field the model uses."""
    return (
        getattr(teacher, "phone", None)
        or getattr(teacher, "phone_number", None)
        or getattr(teacher, "mobile", None)
        or getattr(teacher, "mobile_number", None)
    )


# ==================================================
# LIST / DETAIL / UPDATE / DELETE
# ==================================================
class TeacherPassListView(APIView):
    def get(self, request):
        teacher_passes = TeacherPass.objects.all()
        serializer = TeacherPassSerializer(teacher_passes, many=True)
        return Response(
            {
                "success": True,
                "count": teacher_passes.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class TeacherPassDetailView(APIView):
    def get_object(self, pk):
        try:
            return TeacherPass.objects.get(pk=pk)
        except TeacherPass.DoesNotExist:
            return None

    def get(self, request, pk):
        tp = self.get_object(pk)
        if not tp:
            return Response(
                {"success": False, "message": "Teacher pass not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"success": True, "data": TeacherPassSerializer(tp).data},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        tp = self.get_object(pk)
        if not tp:
            return Response(
                {"success": False, "message": "Teacher pass not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TeacherPassUpdateSerializer(tp, data=request.data, partial=True)
        if serializer.is_valid():
            updated = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Teacher pass updated successfully",
                    "data": TeacherPassSerializer(updated).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        tp = self.get_object(pk)
        if not tp:
            return Response(
                {"success": False, "message": "Teacher pass not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        tp.delete()
        return Response(
            {"success": True, "message": "Teacher pass deleted successfully"},
            status=status.HTTP_200_OK,
        )


# ==================================================
# LOGIN
# ==================================================
class TeacherPassLoginView(APIView):
    def post(self, request):
        serializer = TeacherPassLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        card = serializer.validated_data["teacher_id_card"]
        pwd = serializer.validated_data["password"]

        try:
            tp = TeacherPass.objects.get(teacher_id_card=card, is_active=True)
        except TeacherPass.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Invalid teacher ID card or account inactive",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # check_password() only matches the CURRENT hash.
        # After password reset, the old password can never match.
        if not tp.check_password(pwd):
            return Response(
                {"success": False, "message": "Invalid password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tp.last_login = timezone.now()
        tp.save(update_fields=["last_login", "updated_at"])

        return Response(
            {
                "success": True,
                "message": "Login successful",
                "data": TeacherPassSerializer(tp).data,
            },
            status=status.HTTP_200_OK,
        )


# ==================================================
# STEP 1 — SEND OTP (WhatsApp only)
# ==================================================
class TeacherRequestForgotPasswordOtpView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_send"   # 5/hour — from settings

    def post(self, request):
        serializer = TeacherRequestForgotPasswordOtpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        card = serializer.validated_data["teacher_id_card"]
        dob = serializer.validated_data["dob"]

        try:
            tp = TeacherPass.objects.get(teacher_id_card=card, is_active=True)
        except TeacherPass.DoesNotExist:
            return Response(
                {"success": False, "message": "Teacher pass not found or inactive"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if tp.teacher.dob != dob:
            return Response(
                {"success": False, "message": "Invalid DOB for this Teacher ID card"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone = _get_teacher_phone(tp.teacher)
        if not phone:
            return Response(
                {"success": False, "message": "Teacher phone number not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Resend cooldown
        if cache.get(_cooldown_key(card)):
            return Response(
                {
                    "success": False,
                    "message": "Please wait before requesting another OTP",
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Generate OTP
        otp = f"{random.randint(100000, 999999)}"
        cache.set(_otp_key(card), otp, timeout=OTP_TTL_SECONDS)

        # Send via WhatsApp (reuses the existing generic send_otp method)
        name = f"{tp.teacher.first_name} {tp.teacher.last_name}"
        result = WhatsAppService().send_otp(
            phone_number=phone,
            otp=otp,
            student_name=name,           # param name kept for backward compat
            expiry_minutes=OTP_TTL_SECONDS // 60,
        )

        if not result.get("success"):
            cache.delete(_otp_key(card))
            logger.error(f"Teacher OTP WhatsApp send failed for {card}: {result}")
            return Response(
                {
                    "success": False,
                    "message": "WhatsApp pe OTP bhejne me problem aayi. Please try again.",
                    "error": result.get("error"),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        cache.set(_cooldown_key(card), True, timeout=OTP_RESEND_COOLDOWN)

        return Response(
            {
                "success": True,
                "message": f"OTP sent on WhatsApp to the registered number for {name}",
                "expires_in_seconds": OTP_TTL_SECONDS,
            },
            status=status.HTTP_200_OK,
        )


# ==================================================
# STEP 2 — VERIFY OTP + RESET PASSWORD
# ==================================================
class TeacherVerifyOtpAndResetPasswordView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_verify"   # 10/hour

    def post(self, request):
        serializer = TeacherVerifyOtpAndResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        card = serializer.validated_data["teacher_id_card"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        cached_otp = cache.get(_otp_key(card))
        if not cached_otp or cached_otp != otp:
            return Response(
                {"success": False, "message": "Invalid or expired OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            tp = TeacherPass.objects.get(teacher_id_card=card, is_active=True)
        except TeacherPass.DoesNotExist:
            return Response(
                {"success": False, "message": "Teacher pass not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # set_password(new) re-hashes with a fresh salt →
        # old password never matches again.
        tp.set_password(new_password)
        tp.save()

        cache.delete(_otp_key(card))
        cache.delete(_cooldown_key(card))

        return Response(
            {
                "success": True,
                "message": "Password updated successfully. Please login with your new password.",
            },
            status=status.HTTP_200_OK,
        )


# ==================================================
# LOGOUT
# ==================================================
class TeacherPassLogoutView(APIView):
    def post(self, request):
        card = request.data.get("teacher_id_card")
        if not card:
            return Response(
                {"success": False, "message": "teacher_id_card is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            TeacherPass.objects.get(teacher_id_card=card)
            # If you use JWT/Knox later — blacklist token here
            return Response(
                {"success": True, "message": "Logged out successfully"},
                status=status.HTTP_200_OK,
            )
        except TeacherPass.DoesNotExist:
            return Response(
                {"success": False, "message": "Teacher pass not found"},
                status=status.HTTP_404_NOT_FOUND,
            )