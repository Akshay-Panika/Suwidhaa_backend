from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Teacher
from .serializers import TeacherSerializer


class TeacherCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = TeacherSerializer(data=request.data)

        if serializer.is_valid():
            teacher = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Teacher created successfully",
                    "data": TeacherSerializer(teacher).data,
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
                {
                    "success": False,
                    "message": "Teacher not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "data": TeacherSerializer(teacher).data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        teacher = self.get_object(pk)

        if not teacher:
            return Response(
                {
                    "success": False,
                    "message": "Teacher not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TeacherSerializer(
            teacher,
            data=request.data,
        )

        if serializer.is_valid():
            teacher = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Teacher updated successfully",
                    "data": TeacherSerializer(teacher).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        teacher = self.get_object(pk)

        if not teacher:
            return Response(
                {
                    "success": False,
                    "message": "Teacher not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TeacherSerializer(
            teacher,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            teacher = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Teacher updated successfully",
                    "data": TeacherSerializer(teacher).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        teacher = self.get_object(pk)

        if not teacher:
            return Response(
                {
                    "success": False,
                    "message": "Teacher not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        teacher.delete()

        return Response(
            {
                "success": True,
                "message": "Teacher deleted successfully",
            },
            status=status.HTTP_200_OK,
        )