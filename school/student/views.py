from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Student
from .serializers import StudentSerializer
from school.student_pass.models import StudentPass  # Import StudentPass


class StudentCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def generate_student_id_card(self):
        """Generate unique student ID card like student-01, student-02, etc."""
        # Get all existing student ID cards
        existing_ids = Student.objects.filter(
            student_id_card__isnull=False
        ).values_list('student_id_card', flat=True)
        
        # Also check student_pass table for any existing IDs
        existing_pass_ids = StudentPass.objects.filter(
            student_id_card__isnull=False
        ).values_list('student_id_card', flat=True)
        
        # Combine both sets of existing IDs
        all_existing_ids = set(existing_ids) | set(existing_pass_ids)
        
        # Start from 1 and find the first available number
        counter = 1
        while True:
            new_id = f"student-{str(counter).zfill(2)}"
            if new_id not in all_existing_ids:
                return new_id
            counter += 1

    def post(self, request):
        # Generate unique student_id_card before creating student
        student_id_card = self.generate_student_id_card()
        
        # Add student_id_card to request data
        request.data._mutable = True
        request.data['student_id_card'] = student_id_card
        request.data._mutable = False
        
        serializer = StudentSerializer(data=request.data)

        if serializer.is_valid():
            try:
                student = serializer.save()
                
                # Create student pass with the same student_id_card
                student_pass = StudentPass.objects.create(
                    student=student,
                    student_id_card=student_id_card
                )
                
                # Prepare response with student pass data
                student_data = StudentSerializer(student).data
                student_data['student_pass'] = {
                    'id': student_pass.id,
                    'student_id_card': student_pass.student_id_card,
                    'is_active': student_pass.is_active,
                    'created_at': student_pass.created_at
                }
                
                return Response(
                    {
                        "success": True,
                        "message": "Student created successfully",
                        "data": student_data,
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
        
        # Add student pass info to each student
        data = []
        for student in students:
            student_data = StudentSerializer(student).data
            try:
                student_pass = StudentPass.objects.get(student=student)
                student_data['student_pass'] = {
                    'id': student_pass.id,
                    'student_id_card': student_pass.student_id_card,
                    'is_active': student_pass.is_active,
                }
            except StudentPass.DoesNotExist:
                student_data['student_pass'] = None
            data.append(student_data)

        return Response(
            {
                "success": True,
                "count": students.count(),
                "data": data,
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

        student_data = StudentSerializer(student).data
        
        # Add student pass info
        try:
            student_pass = StudentPass.objects.get(student=student)
            student_data['student_pass'] = {
                'id': student_pass.id,
                'student_id_card': student_pass.student_id_card,
                'is_active': student_pass.is_active,
                'last_login': student_pass.last_login,
                'created_at': student_pass.created_at
            }
        except StudentPass.DoesNotExist:
            student_data['student_pass'] = None

        return Response(
            {
                "success": True,
                "data": student_data,
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

        # Remove student_id_card from request data if present (it's read-only)
        if 'student_id_card' in request.data:
            request.data._mutable = True
            del request.data['student_id_card']
            request.data._mutable = False

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

        # Remove student_id_card from request data if present (it's read-only)
        if 'student_id_card' in request.data:
            request.data._mutable = True
            del request.data['student_id_card']
            request.data._mutable = False

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