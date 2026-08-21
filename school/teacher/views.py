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
            
            # Serialize the created teacher with full data
            response_data = TeacherSerializer(teacher).data

            return Response(
                {
                    "success": True,
                    "message": "Teacher created successfully",
                    "data": response_data,
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

        # Full update - all fields required except those with defaults
        serializer = TeacherSerializer(
            teacher,
            data=request.data,
            partial=False,  # Full update
        )

        if serializer.is_valid():
            updated_teacher = serializer.save()
            
            return Response(
                {
                    "success": True,
                    "message": "Teacher updated successfully",
                    "data": TeacherSerializer(updated_teacher).data,
                    "updated_fields": list(request.data.keys()),  # Track which fields were updated
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

        # Partial update - only provided fields will be updated
        serializer = TeacherSerializer(
            teacher,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            updated_teacher = serializer.save()
            
            # Get list of fields that were actually updated
            updated_fields = []
            for field, value in request.data.items():
                if hasattr(teacher, field):
                    old_value = getattr(teacher, field)
                    new_value = getattr(updated_teacher, field)
                    if old_value != new_value:
                        updated_fields.append(field)
            
            return Response(
                {
                    "success": True,
                    "message": "Teacher updated successfully",
                    "data": TeacherSerializer(updated_teacher).data,
                    "updated_fields": updated_fields,
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

        # Store teacher name for response before deletion
        teacher_name = str(teacher)
        teacher.delete()

        return Response(
            {
                "success": True,
                "message": f"Teacher '{teacher_name}' deleted successfully",
            },
            status=status.HTTP_200_OK,
        )