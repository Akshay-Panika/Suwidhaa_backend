from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import random
import logging

from .models import StudentPass
from .serializers import (
    StudentPassSerializer,
    StudentPassUpdateSerializer,
    StudentPassLoginSerializer,
    RequestForgotPasswordOtpSerializer,
    VerifyOtpAndResetPasswordSerializer
)
from services.whatsapp_service import WhatsAppService  # Apne project ke hisaab se import rakhein

logger = logging.getLogger(__name__)

# Temporary cache dictionary for OTPs (Production me Redis ya Django Cache use karein)
OTP_CACHE = {}


class StudentPassListView(APIView):
    def get(self, request):
        student_passes = StudentPass.objects.all()
        serializer = StudentPassSerializer(student_passes, many=True)
        return Response(
            {"success": True, "count": student_passes.count(), "data": serializer.data},
            status=status.HTTP_200_OK
        )


class StudentPassDetailView(APIView):
    def get_object(self, pk):
        try:
            return StudentPass.objects.get(pk=pk)
        except StudentPass.DoesNotExist:
            return None
    
    def get(self, request, pk):
        student_pass = self.get_object(pk)
        if not student_pass:
            return Response({"success": False, "message": "Student pass not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "data": StudentPassSerializer(student_pass).data}, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        student_pass = self.get_object(pk)
        if not student_pass:
            return Response({"success": False, "message": "Student pass not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentPassUpdateSerializer(student_pass, data=request.data, partial=True)
        if serializer.is_valid():
            updated_pass = serializer.save()
            return Response({
                "success": True,
                "message": "Student pass updated successfully",
                "data": StudentPassSerializer(updated_pass).data
            }, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        student_pass = self.get_object(pk)
        if not student_pass:
            return Response({"success": False, "message": "Student pass not found"}, status=status.HTTP_404_NOT_FOUND)
        student_pass.delete()
        return Response({"success": True, "message": "Student pass deleted successfully"}, status=status.HTTP_200_OK)


class StudentPassLoginView(APIView):
    def post(self, request):
        serializer = StudentPassLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        student_id_card = serializer.validated_data['student_id_card']
        password = serializer.validated_data['password']
        
        try:
            student_pass = StudentPass.objects.get(student_id_card=student_id_card, is_active=True)
            
            if student_pass.check_password(password):
                student_pass.last_login = datetime.now()
                student_pass.save()
                
                return Response({
                    "success": True,
                    "message": "Login successful",
                    "data": StudentPassSerializer(student_pass).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
        except StudentPass.DoesNotExist:
            return Response({"success": False, "message": "Invalid student ID card or account inactive"}, status=status.HTTP_404_NOT_FOUND)


# 1️⃣ Step 1: Request OTP for Forgot Password
class RequestForgotPasswordOtpView(APIView):
    def post(self, request):
        serializer = RequestForgotPasswordOtpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        student_id_card = serializer.validated_data['student_id_card']
        dob = serializer.validated_data['dob']
        
        try:
            student_pass = StudentPass.objects.get(student_id_card=student_id_card, is_active=True)
            
            # Verify DOB
            if student_pass.student.dob != dob:
                return Response({"success": False, "message": "Invalid DOB for this student ID card"}, status=status.HTTP_400_BAD_REQUEST)
            
            parent_phone = student_pass.student.parent_phone
            if not parent_phone:
                return Response({"success": False, "message": "Parent phone number not available for this student"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate 6-digit OTP
            otp = str(random.randint(100000, 999999))
            OTP_CACHE[student_id_card] = otp  # Cache me store karein
            
            # Send OTP via WhatsApp
            whatsapp_service = WhatsAppService()
            student_name = f"{student_pass.student.first_name} {student_pass.student.last_name}"
            
            # Aap apna whatsapp service method call kar sakte hain jo OTP bhej sake
            # Example: whatsapp_service.send_otp(phone_number=parent_phone, otp=otp, student_name=student_name)
            
            return Response({
                "success": True,
                "message": f"OTP sent successfully to registered phone number for {student_name}",
                "debug_otp": otp  # Testing ke liye response me dikha rahe hain, production me hata dein
            }, status=status.HTTP_200_OK)
            
        except StudentPass.DoesNotExist:
            return Response({"success": False, "message": "Student pass not found or inactive"}, status=status.HTTP_404_NOT_FOUND)


# 2️⃣ Step 2: Verify OTP & Save Custom New Password
class VerifyOtpAndResetPasswordView(APIView):
    def post(self, request):
        serializer = VerifyOtpAndResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        student_id_card = serializer.validated_data['student_id_card']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        
        # Check cached OTP
        cached_otp = OTP_CACHE.get(student_id_card)
        if not cached_otp or cached_otp != otp:
            return Response({"success": False, "message": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student_pass = StudentPass.objects.get(student_id_card=student_id_card, is_active=True)
            
            # Set student's custom password
            student_pass.set_password(new_password)
            student_pass.save()
            
            # Clear OTP from cache after successful reset
            del OTP_CACHE[student_id_card]
            
            return Response({
                "success": True,
                "message": "Password updated successfully with your new password!"
            }, status=status.HTTP_200_OK)
            
        except StudentPass.DoesNotExist:
            return Response({"success": False, "message": "Student pass not found"}, status=status.HTTP_404_NOT_FOUND)


# 3️⃣ Logout API View
class StudentPassLogoutView(APIView):
    def post(self, request):
        student_id_card = request.data.get('student_id_card')
        
        if not student_id_card:
            return Response({"success": False, "message": "student_id_card is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            student_pass = StudentPass.objects.get(student_id_card=student_id_card)
            # Yahan agar token-based authentication (jaise Knox/JWT) use kar rahe hain toh token blacklist/delete kar sakte hain.
            
            return Response({
                "success": True,
                "message": "Logged out successfully"
            }, status=status.HTTP_200_OK)
        except StudentPass.DoesNotExist:
            return Response({"success": False, "message": "Student pass not found"}, status=status.HTTP_404_NOT_FOUND)