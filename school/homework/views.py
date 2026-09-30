from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import logging
import json

from .models import Homework, HomeworkStudent
from .serializers import HomeworkSerializer, HomeworkStudentSerializer

logger = logging.getLogger(__name__)


def _parse_students(data):
 
    students = data.get('students')
    
    # ✅ FIX: agar students field hai hi nahi, toh kuch mat karo
    if students is None:
        return data
    
    # ✅ FIX: agar string hai toh JSON parse karo
    if isinstance(students, str):
        # Khaali string ho toh skip karo
        if students.strip() == "":
            return data
        try:
            data['students'] = json.loads(students)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for 'students' field.")
    
    return data

class HomeworkCreateView(APIView):
    """
    POST: Create new homework (with required students list)
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        # ✅ FIX: Parse students JSON string (form-data ke liye)
        data = request.data.copy()
        try:
            data = _parse_students(data)
        except ValueError as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        required_fields = [
            'subject_name', 'subject_topic', 'issue_date', 'end_date',
            'class_name', 'teacher_name', 'teacher_id', 'school_type'
        ]
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return Response({
                "success": False,
                "message": f"Required fields missing: {', '.join(missing)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = HomeworkSerializer(data=data)
        if serializer.is_valid():
            try:
                homework = serializer.save()
                return Response({
                    "success": True,
                    "message": "Homework created successfully",
                    "data": HomeworkSerializer(homework).data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Failed to create homework: {str(e)}")
                return Response({
                    "success": False,
                    "message": f"Failed to create homework: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class HomeworkListView(APIView):
    """
    GET: List all homework (each with nested students + status)
    """
    def get(self, request):
        queryset = Homework.objects.all().prefetch_related('students')

        class_name     = request.query_params.get('class_name')
        school_type    = request.query_params.get('school_type')
        teacher_id     = request.query_params.get('teacher_id')
        student_id     = request.query_params.get('student_id')
        student_class  = request.query_params.get('student_class')
        student_status = request.query_params.get('student_status')

        if class_name:
            queryset = queryset.filter(class_name__iexact=class_name)
        if school_type:
            queryset = queryset.filter(school_type__iexact=school_type)
        if teacher_id:
            queryset = queryset.filter(teacher_id__iexact=teacher_id)
        if student_id:
            queryset = queryset.filter(students__student_id__iexact=student_id).distinct()
        if student_class:
            queryset = queryset.filter(students__student_class__iexact=student_class).distinct()
        if student_status is not None:
            is_true = student_status.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(students__status=is_true).distinct()

        queryset = queryset.order_by("-id")
        serializer = HomeworkSerializer(queryset, many=True)

        return Response({
            "success": True,
            "count": queryset.count(),
            "filters": {
                "class_name": class_name,
                "school_type": school_type,
                "teacher_id": teacher_id,
                "student_id": student_id,
                "student_class": student_class,
                "student_status": student_status,
            },
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class HomeworkByTeacherView(APIView):
    """
    GET: List homework for a specific teacher_id
    """
    def get(self, request, teacher_id):
        homework = Homework.objects.filter(
            teacher_id__iexact=teacher_id
        ).prefetch_related('students').order_by("-id")

        serializer = HomeworkSerializer(homework, many=True)

        return Response({
            "success": True,
            "teacher_id": teacher_id,
            "count": homework.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class HomeworkDetailView(APIView):
    """
    GET / PUT / PATCH / DELETE
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return Homework.objects.prefetch_related('students').get(pk=pk)
        except Homework.DoesNotExist:
            return None

    def get(self, request, pk):
        hw = self.get_object(pk)
        if not hw:
            return Response({"success": False, "message": "Homework not found"},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "data": HomeworkSerializer(hw).data},
                        status=status.HTTP_200_OK)

    def put(self, request, pk):
        hw = self.get_object(pk)
        if not hw:
            return Response({"success": False, "message": "Homework not found"},
                            status=status.HTTP_404_NOT_FOUND)

        # ✅ FIX: Parse students JSON string
        data = request.data.copy()
        try:
            data = _parse_students(data)
        except ValueError as e:
            return Response({"success": False, "message": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        required = ['subject_name', 'subject_topic', 'issue_date', 'end_date',
                    'class_name', 'teacher_name', 'teacher_id', 'school_type']
        missing = [f for f in required if not data.get(f)]
        if missing:
            return Response({
                "success": False,
                "message": f"Required fields missing: {', '.join(missing)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = HomeworkSerializer(hw, data=data)
        if serializer.is_valid():
            try:
                hw = serializer.save()
                return Response({
                    "success": True,
                    "message": "Homework updated successfully",
                    "data": HomeworkSerializer(hw).data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Failed to update homework: {str(e)}")
                return Response({"success": False,
                                 "message": f"Failed to update homework: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"success": False, "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        hw = self.get_object(pk)
        if not hw:
            return Response({"success": False, "message": "Homework not found"},
                            status=status.HTTP_404_NOT_FOUND)

        # ✅ FIX: Parse students JSON string (agar bheja gaya ho)
        data = request.data.copy()
        if 'students' in data:
            try:
                data = _parse_students(data)
            except ValueError as e:
                return Response({"success": False, "message": str(e)},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = HomeworkSerializer(hw, data=data, partial=True)
        if serializer.is_valid():
            try:
                hw = serializer.save()
                return Response({
                    "success": True,
                    "message": "Homework updated successfully",
                    "data": HomeworkSerializer(hw).data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Failed to update homework: {str(e)}")
                return Response({"success": False,
                                 "message": f"Failed to update homework: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"success": False, "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        hw = self.get_object(pk)
        if not hw:
            return Response({"success": False, "message": "Homework not found"},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            hw.delete()
            return Response({"success": True, "message": "Homework deleted successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to delete homework: {str(e)}")
            return Response({"success": False,
                             "message": f"Failed to delete homework: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ⬇️ TOGGLE endpoint (per student)
class HomeworkStudentToggleView(APIView):
    """
    PATCH: Toggle a single student's status (true <-> false)
    URL: /homework/<homework_id>/students/<student_pk>/toggle/
    """
    def patch(self, request, homework_id, student_pk):
        try:
            student = HomeworkStudent.objects.get(
                pk=student_pk, homework_id=homework_id
            )
        except HomeworkStudent.DoesNotExist:
            return Response({
                "success": False,
                "message": "Student record not found for this homework"
            }, status=status.HTTP_404_NOT_FOUND)

        student.status = not student.status
        student.save()

        return Response({
            "success": True,
            "message": f"Status toggled to {student.status}",
            "data": HomeworkStudentSerializer(student).data
        }, status=status.HTTP_200_OK)