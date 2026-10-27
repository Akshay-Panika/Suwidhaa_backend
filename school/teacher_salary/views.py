from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from school.teacher.models import Teacher
from .serializers import TeacherSalaryListSerializer

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