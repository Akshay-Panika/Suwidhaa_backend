from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from .models import StudentPass
from .serializers import (
    StudentPassSerializer,
    StudentPassUpdateSerializer,
    StudentPassLoginSerializer,
    StudentPassForgotPasswordSerializer
)


class StudentPassListView(APIView):
    """List all student passes"""
    
    def get(self, request):
        student_passes = StudentPass.objects.all()
        serializer = StudentPassSerializer(student_passes, many=True)
        
        return Response(
            {
                "success": True,
                "count": student_passes.count(),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class StudentPassDetailView(APIView):
    """Get, update, delete student pass by ID"""
    
    def get_object(self, pk):
        try:
            return StudentPass.objects.get(pk=pk)
        except StudentPass.DoesNotExist:
            return None
    
    def get(self, request, pk):
        student_pass = self.get_object(pk)
        
        if not student_pass:
            return Response(
                {
                    "success": False,
                    "message": "Student pass not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StudentPassSerializer(student_pass)
        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    def patch(self, request, pk):
        student_pass = self.get_object(pk)
        
        if not student_pass:
            return Response(
                {
                    "success": False,
                    "message": "Student pass not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StudentPassUpdateSerializer(
            student_pass,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            updated_pass = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Student pass updated successfully",
                    "data": StudentPassSerializer(updated_pass).data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                "success": False,
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request, pk):
        student_pass = self.get_object(pk)
        
        if not student_pass:
            return Response(
                {
                    "success": False,
                    "message": "Student pass not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        student_pass.delete()
        
        return Response(
            {
                "success": True,
                "message": "Student pass deleted successfully"
            },
            status=status.HTTP_200_OK
        )


class StudentPassLoginView(APIView):
    """Login using student_id_card and password"""
    
    def post(self, request):
        serializer = StudentPassLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        student_id_card = serializer.validated_data['student_id_card']
        password = serializer.validated_data['password']
        
        try:
            student_pass = StudentPass.objects.get(student_id_card=student_id_card, is_active=True)
            
            if student_pass.check_password(password):
                student_pass.last_login = datetime.now()
                student_pass.save()
                
                return Response(
                    {
                        "success": True,
                        "message": "Login successful",
                        "data": StudentPassSerializer(student_pass).data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "success": False,
                        "message": "Invalid password"
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except StudentPass.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Invalid student ID card or account inactive"
                },
                status=status.HTTP_404_NOT_FOUND
            )


class StudentPassForgotPasswordView(APIView):
    """Forgot password - Reset password using student_id_card and DOB"""
    
    def post(self, request):
        serializer = StudentPassForgotPasswordSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        student_id_card = serializer.validated_data['student_id_card']
        dob = serializer.validated_data['dob']
        
        try:
            student_pass = StudentPass.objects.get(student_id_card=student_id_card, is_active=True)
            
            # Verify DOB
            if student_pass.student.dob != dob:
                return Response(
                    {
                        "success": False,
                        "message": "Invalid DOB for this student ID card"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Reset password to DOB
            new_password = student_pass.generate_default_password()
            student_pass.set_password(new_password)
            student_pass.save()
            
            return Response(
                {
                    "success": True,
                    "message": "Password reset successfully",
                    "new_password": new_password,
                    "student_id_card": student_pass.student_id_card
                },
                status=status.HTTP_200_OK
            )
            
        except StudentPass.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Student pass not found or inactive"
                },
                status=status.HTTP_404_NOT_FOUND
            )