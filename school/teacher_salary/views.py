# school/teacher_salary/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from school.teacher.models import Teacher
from .serializers import TeacherSalaryListSerializer


# =====================================================================
# 1. LIST ALL TEACHERS
#    GET /api/v1/school/teacher/salary/list/
# =====================================================================
class TeacherSalaryListView(APIView):
    def get(self, request):
        teachers = Teacher.objects.select_related("school").all().order_by("-id")
        serializer = TeacherSalaryListSerializer(teachers, many=True)

        return Response(
            {
                "success": True,
                "count": teachers.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =====================================================================
# 2. LIST TEACHERS BY SCHOOL
#    GET /api/v1/school/teacher/salary/list/school/<school_id>/
# =====================================================================
class TeacherSalaryListBySchoolView(APIView):
    def get(self, request, school_id):
        teachers = (
            Teacher.objects.filter(school_id=school_id)
            .select_related("school")
            .order_by("-id")
        )

        if not teachers.exists():
            return Response(
                {
                    "success": False,
                    "message": f"No teachers found for school id '{school_id}'",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TeacherSalaryListSerializer(teachers, many=True)

        return Response(
            {
                "success": True,
                "school_id": school_id,
                "count": teachers.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )