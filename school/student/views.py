from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Student
from .serializers import StudentSerializer
from school.student_pass.models import StudentPass  # Import StudentPass


class StudentCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = StudentSerializer(data=request.data)

        if serializer.is_valid():
            student = serializer.save()
            
            # Auto-create student pass
            try:
                StudentPass.objects.create(student=student)
                
                return Response(
                    {
                        "success": True,
                        "message": "Student created successfully",
                        "data": StudentSerializer(student).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                # If student pass creation fails, delete the student
                student.delete()
                return Response(
                    {
                        "success": False,
                        "message": f"Failed to create student pass: {str(e)}"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class StudentListView(APIView):
    def get(self, request):
        students = Student.objects.all().order_by("-id")
        serializer = StudentSerializer(students, many=True)

        return Response(
            {
                "success": True,
                "count": students.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


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
            return Response(
                {
                    "success": False,
                    "message": "Student not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "data": StudentSerializer(student).data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        student = self.get_object(pk)

        if not student:
            return Response(
                {
                    "success": False,
                    "message": "Student not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = StudentSerializer(
            student,
            data=request.data,
        )

        if serializer.is_valid():
            student = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Student updated successfully",
                    "data": StudentSerializer(student).data,
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
        student = self.get_object(pk)

        if not student:
            return Response(
                {
                    "success": False,
                    "message": "Student not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = StudentSerializer(
            student,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            student = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Student updated successfully",
                    "data": StudentSerializer(student).data,
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
        student = self.get_object(pk)

        if not student:
            return Response(
                {
                    "success": False,
                    "message": "Student not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Also delete student pass
        try:
            student_pass = StudentPass.objects.get(student=student)
            student_pass.delete()
        except StudentPass.DoesNotExist:
            pass

        student.delete()

        return Response(
            {
                "success": True,
                "message": "Student deleted successfully",
            },
            status=status.HTTP_200_OK,
        )