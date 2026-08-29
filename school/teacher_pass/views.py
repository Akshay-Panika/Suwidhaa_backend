from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from .models import TeacherPass
from .serializers import (
    TeacherPassSerializer,
    TeacherPassUpdateSerializer,
    TeacherPassLoginSerializer,
    TeacherPassForgotPasswordSerializer
)


class TeacherPassListView(APIView):
    def get(self, request):
        teacher_passes = TeacherPass.objects.all()
        serializer = TeacherPassSerializer(teacher_passes, many=True)
        
        return Response(
            {
                "success": True,
                "count": teacher_passes.count(),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class TeacherPassDetailView(APIView):
    def get_object(self, pk):
        try:
            return TeacherPass.objects.get(pk=pk)
        except TeacherPass.DoesNotExist:
            return None
    
    def get(self, request, pk):
        teacher_pass = self.get_object(pk)
        
        if not teacher_pass:
            return Response(
                {"success": False, "message": "Teacher pass not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TeacherPassSerializer(teacher_pass)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )
    
    def patch(self, request, pk):
        teacher_pass = self.get_object(pk)
        
        if not teacher_pass:
            return Response(
                {"success": False, "message": "Teacher pass not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TeacherPassUpdateSerializer(
            teacher_pass,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            updated_pass = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Teacher pass updated successfully",
                    "data": TeacherPassSerializer(updated_pass).data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request, pk):
        teacher_pass = self.get_object(pk)
        
        if not teacher_pass:
            return Response(
                {"success": False, "message": "Teacher pass not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        teacher_pass.delete()
        
        return Response(
            {"success": True, "message": "Teacher pass deleted successfully"},
            status=status.HTTP_200_OK
        )


class TeacherPassLoginView(APIView):
    def post(self, request):
        serializer = TeacherPassLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        teacher_id_card = serializer.validated_data['teacher_id_card']
        password = serializer.validated_data['password']
        
        try:
            teacher_pass = TeacherPass.objects.get(teacher_id_card=teacher_id_card, is_active=True)
            
            if teacher_pass.check_password(password):
                teacher_pass.last_login = datetime.now()
                teacher_pass.save()
                
                return Response(
                    {
                        "success": True,
                        "message": "Login successful",
                        "data": TeacherPassSerializer(teacher_pass).data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"success": False, "message": "Invalid password"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except TeacherPass.DoesNotExist:
            return Response(
                {"success": False, "message": "Invalid Teacher ID Card or account inactive"},
                status=status.HTTP_404_NOT_FOUND
            )


class TeacherPassForgotPasswordView(APIView):
    def post(self, request):
        serializer = TeacherPassForgotPasswordSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        teacher_id_card = serializer.validated_data['teacher_id_card']
        dob = serializer.validated_data['dob']
        
        try:
            teacher_pass = TeacherPass.objects.get(teacher_id_card=teacher_id_card, is_active=True)
            
            if teacher_pass.teacher.dob != dob:
                return Response(
                    {"success": False, "message": "Invalid DOB for this Teacher ID Card"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            new_password = teacher_pass.generate_default_password()
            teacher_pass.set_password(new_password)
            teacher_pass.save()
            
            return Response(
                {
                    "success": True,
                    "message": "Password reset successfully",
                    "new_password": new_password,
                    "teacher_id_card": teacher_pass.teacher_id_card
                },
                status=status.HTTP_200_OK
            )
            
        except TeacherPass.DoesNotExist:
            return Response(
                {"success": False, "message": "Teacher pass not found or inactive"},
                status=status.HTTP_404_NOT_FOUND
            )