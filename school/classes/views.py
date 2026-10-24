# school/classes/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from .models import Class
from .serializers import ClassSerializer
from school.teacher.models import Teacher


class ClassCreateView(APIView):
    """
    POST /class/create/
    Body:
      {
        "class_name": "5A",
        "school_id": 1,
        "sections": ["A","B"],
        "check_box": true
      }

    (teacher is optional — usually assigned later via assign-teacher API)
    """
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = ClassSerializer(data=request.data)

        if serializer.is_valid():
            class_instance = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Class created successfully",
                    "data": ClassSerializer(class_instance).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ClassBySchoolView(APIView):
    """
    GET /class/list/school/<school_id>/
    Returns all classes for a given school.
    """
    def get(self, request, school_id):
        classes = (
            Class.objects
            .select_related("school", "class_teacher")
            .filter(school_id=school_id)
            .order_by("-id")
        )

        if not classes.exists():
            return Response(
                {
                    "success": False,
                    "message": f"No classes found for school id '{school_id}'",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ClassSerializer(classes, many=True)
        return Response(
            {
                "success": True,
                "school_id": school_id,
                "count": classes.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class AssignClassTeacherView(APIView):
    """
    POST /class/<pk>/assign-teacher/
    Body: { "teacher_id": 7 }

    - Assigns the given teacher as class teacher.
    - Validates the teacher belongs to the same school.
    - Send teacher_id = null to un-assign.
    """
    parser_classes = [JSONParser]

    def post(self, request, pk):
        try:
            class_instance = Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            return Response(
                {"success": False, "message": "Class not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        teacher_id = request.data.get("teacher_id")

        # Un-assign
        if teacher_id in (None, "", 0):
            class_instance.class_teacher = None
            class_instance.save()
            return Response(
                {
                    "success": True,
                    "message": "Class teacher un-assigned",
                    "data": ClassSerializer(class_instance).data,
                },
                status=status.HTTP_200_OK,
            )

        try:
            teacher = Teacher.objects.get(pk=teacher_id)
        except Teacher.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": f"Teacher with id '{teacher_id}' not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Teacher must belong to the same school as the class
        if class_instance.school and teacher.school_id != class_instance.school_id:
            return Response(
                {
                    "success": False,
                    "message": "Teacher does not belong to this class's school.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        class_instance.class_teacher = teacher
        class_instance.save()

        return Response(
            {
                "success": True,
                "message": "Class teacher assigned successfully",
                "data": ClassSerializer(class_instance).data,
            },
            status=status.HTTP_200_OK,
        )