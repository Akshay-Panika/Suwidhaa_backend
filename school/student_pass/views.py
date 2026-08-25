from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from .models import StudentPass
from .serializers import StudentPassSerializer, StudentPassLoginSerializer


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
        
        serializer = StudentPassSerializer(
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
                        "data": {
                            "student_pass": StudentPassSerializer(student_pass).data,
                            "student": {
                                "id": student_pass.student.id,
                                "name": f"{student_pass.student.first_name} {student_pass.student.last_name}",
                                "class": student_pass.student.student_class,
                                "email": getattr(student_pass.student, 'email', None)
                            }
                        }
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