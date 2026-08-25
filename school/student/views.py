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
        # Check if student_id_card is provided in request
        student_id_card = request.data.get('student_id_card')
        
        if not student_id_card:
            return Response(
                {
                    "success": False,
                    "message": "student_id_card is required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Check if student_id_card already exists in Student model
        if Student.objects.filter(student_id_card=student_id_card).exists():
            return Response(
                {
                    "success": False,
                    "message": f"Student with ID card '{student_id_card}' already exists"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Check if student_id_card already exists in StudentPass model
        if StudentPass.objects.filter(student_id_card=student_id_card).exists():
            return Response(
                {
                    "success": False,
                    "message": f"Student ID card '{student_id_card}' already exists in student pass"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = StudentSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Save student with provided student_id_card
                student = serializer.save()
                
                # Create student pass with the same student_id_card
                StudentPass.objects.create(
                    student=student,
                    student_id_card=student_id_card
                )
                
                return Response(
                    {
                        "success": True,
                        "message": "Student created successfully",
                        "data": StudentSerializer(student).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
                
            except Exception as e:
                # If anything fails, delete the student
                if 'student' in locals():
                    student.delete()
                return Response(
                    {
                        "success": False,
                        "message": f"Failed to create student: {str(e)}"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(
            {
                "success": False,
                "message": "Validation failed",
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

        # Check if student_id_card is being updated
        if 'student_id_card' in request.data:
            new_card = request.data.get('student_id_card')
            
            # Check if new card already exists (excluding current student)
            if Student.objects.filter(student_id_card=new_card).exclude(id=pk).exists():
                return Response(
                    {
                        "success": False,
                        "message": f"Student ID card '{new_card}' already exists"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            if StudentPass.objects.filter(student_id_card=new_card).exclude(student_id=pk).exists():
                return Response(
                    {
                        "success": False,
                        "message": f"Student ID card '{new_card}' already exists in student pass"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = StudentSerializer(
            student,
            data=request.data,
        )

        if serializer.is_valid():
            student = serializer.save()
            
            # Update student pass if student_id_card was changed
            if 'student_id_card' in request.data:
                try:
                    student_pass = StudentPass.objects.get(student=student)
                    student_pass.student_id_card = request.data['student_id_card']
                    student_pass.save()
                except StudentPass.DoesNotExist:
                    pass

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

        # Check if student_id_card is being updated
        if 'student_id_card' in request.data:
            new_card = request.data.get('student_id_card')
            
            # Check if new card already exists (excluding current student)
            if Student.objects.filter(student_id_card=new_card).exclude(id=pk).exists():
                return Response(
                    {
                        "success": False,
                        "message": f"Student ID card '{new_card}' already exists"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            if StudentPass.objects.filter(student_id_card=new_card).exclude(student_id=pk).exists():
                return Response(
                    {
                        "success": False,
                        "message": f"Student ID card '{new_card}' already exists in student pass"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = StudentSerializer(
            student,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            student = serializer.save()
            
            # Update student pass if student_id_card was changed
            if 'student_id_card' in request.data:
                try:
                    student_pass = StudentPass.objects.get(student=student)
                    student_pass.student_id_card = request.data['student_id_card']
                    student_pass.save()
                except StudentPass.DoesNotExist:
                    pass

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