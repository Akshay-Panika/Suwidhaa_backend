from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from school.teacher.models import Teacher
from .serializers import TeacherSalaryListSerializer, TeacherSalaryTransactionCreateSerializer


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


class TeacherSalaryTransactionCreateView(APIView):
    def post(self, request):
        serializer = TeacherSalaryTransactionCreateSerializer(data=request.data)

        if serializer.is_valid():
            transaction = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Salary transaction recorded successfully",
                    "data": TeacherSalaryTransactionCreateSerializer(transaction).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )