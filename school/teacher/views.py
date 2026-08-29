from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import logging
from datetime import date

from .models import Teacher
from .serializers import TeacherSerializer
from school.teacher_pass.models import TeacherPass
from services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)


class TeacherCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        teacher_id_card = request.data.get('teacher_id_card')
        
        if not teacher_id_card:
            return Response(
                {"success": False, "message": "teacher_id_card is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if Teacher.objects.filter(teacher_id_card=teacher_id_card).exists():
            return Response(
                {"success": False, "message": f"Teacher with ID card '{teacher_id_card}' already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if TeacherPass.objects.filter(teacher_id_card=teacher_id_card).exists():
            return Response(
                {"success": False, "message": f"Teacher ID card '{teacher_id_card}' already exists in teacher pass"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TeacherSerializer(data=request.data)

        if serializer.is_valid():
            try:
                teacher = serializer.save()
                
                default_password = teacher.dob.strftime('%Y%m%d') if teacher.dob else date.today().strftime('%Y%m%d')
                
                teacher_pass = TeacherPass.objects.create(
                    teacher=teacher,
                    teacher_id_card=teacher_id_card
                )
                teacher_pass.set_password(default_password)
                teacher_pass.save()
                
                whatsapp_response = None
                if teacher.phone:
                    whatsapp_service = WhatsAppService()
                    teacher_name = f"{teacher.first_name} {teacher.last_name}"
                    whatsapp_response = whatsapp_service.send_student_credentials(
                        phone_number=teacher.phone,
                        student_name=teacher_name,
                        student_id=teacher_id_card,
                        password=default_password
                    )
                else:
                    whatsapp_response = {'success': False, 'error': 'No phone number provided'}
                
                return Response(
                    {
                        "success": True,
                        "message": "Teacher created successfully",
                        "data": TeacherSerializer(teacher).data,
                        "whatsapp": whatsapp_response
                    },
                    status=status.HTTP_201_CREATED,
                )
                
            except Exception as e:
                if 'teacher' in locals():
                    teacher.delete()
                logger.error(f"Failed to create teacher: {str(e)}")
                return Response(
                    {"success": False, "message": f"Failed to create teacher: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TeacherListView(APIView):
    def get(self, request):
        teachers = Teacher.objects.all().order_by("-id")
        serializer = TeacherSerializer(teachers, many=True)

        return Response(
            {
                "success": True,
                "count": teachers.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class TeacherDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return Teacher.objects.get(pk=pk)
        except Teacher.DoesNotExist:
            return None

    def get(self, request, pk):
        teacher = self.get_object(pk)

        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"success": True, "data": TeacherSerializer(teacher).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        teacher = self.get_object(pk)

        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if 'teacher_id_card' in request.data:
            new_card = request.data.get('teacher_id_card')
            if Teacher.objects.filter(teacher_id_card=new_card).exclude(id=pk).exists():
                return Response(
                    {"success": False, "message": f"Teacher ID card '{new_card}' already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if TeacherPass.objects.filter(teacher_id_card=new_card).exclude(teacher_id=pk).exists():
                return Response(
                    {"success": False, "message": f"Teacher ID card '{new_card}' already exists in teacher pass"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = TeacherSerializer(teacher, data=request.data)

        if serializer.is_valid():
            teacher = serializer.save()
            
            if 'teacher_id_card' in request.data:
                try:
                    teacher_pass = TeacherPass.objects.get(teacher=teacher)
                    teacher_pass.teacher_id_card = request.data['teacher_id_card']
                    teacher_pass.save()
                except TeacherPass.DoesNotExist:
                    pass

            return Response(
                {
                    "success": True,
                    "message": "Teacher updated successfully",
                    "data": TeacherSerializer(teacher).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        teacher = self.get_object(pk)

        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if 'teacher_id_card' in request.data:
            new_card = request.data.get('teacher_id_card')
            if Teacher.objects.filter(teacher_id_card=new_card).exclude(id=pk).exists():
                return Response(
                    {"success": False, "message": f"Teacher ID card '{new_card}' already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if TeacherPass.objects.filter(teacher_id_card=new_card).exclude(teacher_id=pk).exists():
                return Response(
                    {"success": False, "message": f"Teacher ID card '{new_card}' already exists in teacher pass"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = TeacherSerializer(teacher, data=request.data, partial=True)

        if serializer.is_valid():
            teacher = serializer.save()
            
            if 'teacher_id_card' in request.data:
                try:
                    teacher_pass = TeacherPass.objects.get(teacher=teacher)
                    teacher_pass.teacher_id_card = request.data['teacher_id_card']
                    teacher_pass.save()
                except TeacherPass.DoesNotExist:
                    pass

            return Response(
                {
                    "success": True,
                    "message": "Teacher updated successfully",
                    "data": TeacherSerializer(teacher).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        teacher = self.get_object(pk)

        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            TeacherPass.objects.get(teacher=teacher).delete()
        except TeacherPass.DoesNotExist:
            pass

        teacher.delete()

        return Response(
            {"success": True, "message": "Teacher deleted successfully"},
            status=status.HTTP_200_OK,
        )


# ✅ Teacher Resend WhatsApp Credentials View
class TeacherResendWhatsAppCredentialsView(APIView):
    def post(self, request):
        teacher_id = request.data.get('teacher_id')
        
        if not teacher_id:
            return Response(
                {"success": False, "message": "teacher_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_pass = TeacherPass.objects.get(teacher=teacher)
            
            if not teacher.phone:
                return Response(
                    {"success": False, "message": "Teacher phone number not available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            default_password = teacher.dob.strftime('%Y%m%d') if teacher.dob else date.today().strftime('%Y%m%d')
            whatsapp_service = WhatsAppService()
            teacher_name = f"{teacher.first_name} {teacher.last_name}"
            
            whatsapp_response = whatsapp_service.send_student_credentials(
                phone_number=teacher.phone,
                student_name=teacher_name,
                student_id=teacher_pass.teacher_id_card,
                password=default_password
            )
            
            return Response(
                {
                    "success": whatsapp_response.get('success', False),
                    "message": "WhatsApp message sent successfully" if whatsapp_response.get('success', False) else "Failed to send WhatsApp message",
                    "whatsapp": whatsapp_response
                },
                status=status.HTTP_200_OK if whatsapp_response.get('success', False) else status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        except Teacher.DoesNotExist:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except TeacherPass.DoesNotExist:
            return Response(
                {"success": False, "message": "Teacher pass not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return Response(
                {"success": False, "message": f"Error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )