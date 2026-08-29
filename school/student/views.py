from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import logging
from datetime import date
from .models import Student
from .serializers import StudentSerializer
from school.student_pass.models import StudentPass
from services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)

class StudentCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        student_id_card = request.data.get('student_id_card')
        
        if not student_id_card:
            return Response({"success": False, "message": "student_id_card is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if Student.objects.filter(student_id_card=student_id_card).exists():
            return Response({"success": False, "message": f"Student with ID card '{student_id_card}' already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        if StudentPass.objects.filter(student_id_card=student_id_card).exists():
            return Response({"success": False, "message": f"Student ID card '{student_id_card}' already exists in student pass"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = StudentSerializer(data=request.data)

        if serializer.is_valid():
            try:
                student = serializer.save()
                default_password = student.dob.strftime('%Y%m%d') if student.dob else date.today().strftime('%Y%m%d')
                
                student_pass = StudentPass.objects.create(student=student, student_id_card=student_id_card)
                student_pass.set_password(default_password)
                student_pass.save()
                
                whatsapp_response = None
                if student.parent_phone:
                    whatsapp_service = WhatsAppService()
                    student_name = f"{student.first_name} {student.last_name}"
                    whatsapp_response = whatsapp_service.send_student_credentials(
                        phone_number=student.parent_phone,
                        student_name=student_name,
                        student_id=student_id_card,
                        password=default_password
                    )
                else:
                    whatsapp_response = {'success': False, 'error': 'No parent phone number provided'}
                
                return Response({
                    "success": True,
                    "message": "Student created successfully",
                    "data": StudentSerializer(student).data,
                    "whatsapp": whatsapp_response
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                if 'student' in locals():
                    student.delete()
                logger.error(f"Failed to create student: {str(e)}")
                return Response({"success": False, "message": f"Failed to create student: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"success": False, "message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class StudentListView(APIView):
    def get(self, request):
        students = Student.objects.all().order_by("-id")
        serializer = StudentSerializer(students, many=True)
        return Response({"success": True, "count": students.count(), "data": serializer.data}, status=status.HTTP_200_OK)


class StudentDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return None

    def get(self, request, pk):
        student = self.get_object(pk)
        if not student:
            return Response({"success": False, "message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "data": StudentSerializer(student).data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        student = self.get_object(pk)
        if not student:
            return Response({"success": False, "message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if 'student_id_card' in request.data:
            new_card = request.data.get('student_id_card')
            if Student.objects.filter(student_id_card=new_card).exclude(id=pk).exists():
                return Response({"success": False, "message": f"Student ID card '{new_card}' already exists"}, status=status.HTTP_400_BAD_REQUEST)
            if StudentPass.objects.filter(student_id_card=new_card).exclude(student_id=pk).exists():
                return Response({"success": False, "message": f"Student ID card '{new_card}' already exists in student pass"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            if 'student_id_card' in request.data:
                try:
                    student_pass = StudentPass.objects.get(student=student)
                    student_pass.student_id_card = request.data['student_id_card']
                    student_pass.save()
                except StudentPass.DoesNotExist:
                    pass
            return Response({"success": True, "message": "Student updated successfully", "data": StudentSerializer(student).data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        student = self.get_object(pk)
        if not student:
            return Response({"success": False, "message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if 'student_id_card' in request.data:
            new_card = request.data.get('student_id_card')
            if Student.objects.filter(student_id_card=new_card).exclude(id=pk).exists():
                return Response({"success": False, "message": f"Student ID card '{new_card}' already exists"}, status=status.HTTP_400_BAD_REQUEST)
            if StudentPass.objects.filter(student_id_card=new_card).exclude(student_id=pk).exists():
                return Response({"success": False, "message": f"Student ID card '{new_card}' already exists in student pass"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            student = serializer.save()
            if 'student_id_card' in request.data:
                try:
                    student_pass = StudentPass.objects.get(student=student)
                    student_pass.student_id_card = request.data['student_id_card']
                    student_pass.save()
                except StudentPass.DoesNotExist:
                    pass
            return Response({"success": True, "message": "Student updated successfully", "data": StudentSerializer(student).data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        student = self.get_object(pk)
        if not student:
            return Response({"success": False, "message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            StudentPass.objects.get(student=student).delete()
        except StudentPass.DoesNotExist:
            pass
        student.delete()
        return Response({"success": True, "message": "Student deleted successfully"}, status=status.HTTP_200_OK)


class ResendWhatsAppCredentialsView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        if not student_id:
            return Response({"success": False, "message": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = Student.objects.get(id=student_id)
            student_pass = StudentPass.objects.get(student=student)
            
            if not student.parent_phone:
                return Response({"success": False, "message": "Parent phone number not available"}, status=status.HTTP_400_BAD_REQUEST)
            
            default_password = student.dob.strftime('%Y%m%d') if student.dob else date.today().strftime('%Y%m%d')
            whatsapp_service = WhatsAppService()
            student_name = f"{student.first_name} {student.last_name}"
            
            whatsapp_response = whatsapp_service.send_student_credentials(
                phone_number=student.parent_phone,
                student_name=student_name,
                student_id=student_pass.student_id_card,
                password=default_password
            )
            
            return Response({
                "success": whatsapp_response.get('success', False),
                "message": "WhatsApp message sent successfully" if whatsapp_response.get('success', False) else "Failed to send WhatsApp message",
                "whatsapp": whatsapp_response
            }, status=status.HTTP_200_OK if whatsapp_response.get('success', False) else status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Student.DoesNotExist:
            return Response({"success": False, "message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except StudentPass.DoesNotExist:
            return Response({"success": False, "message": "Student pass not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return Response({"success": False, "message": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)