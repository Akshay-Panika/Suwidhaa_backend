from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from .models import Subject
from .serializers import SubjectSerializer

class SubjectCreateView(APIView):
    """
    POST /subject/create/
    Body: { "name": "Math", "code": "MTH101", "school_id": 1 }
    """
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)

        if serializer.is_valid():
            subject = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Subject created successfully",
                    "data": SubjectSerializer(subject).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SubjectBySchoolView(APIView):
    """
    GET /subject/list/school/<school_id>/
    """
    def get(self, request, school_id):
        subjects = (
            Subject.objects
            .select_related("school")
            .filter(school_id=school_id)
            .order_by("-id")
        )

        if not subjects.exists():
            return Response(
                {
                    "success": False,
                    "message": f"No subjects found for school id '{school_id}'",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SubjectSerializer(subjects, many=True)
        return Response(
            {
                "success": True,
                "school_id": school_id,
                "count": subjects.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ✅ NEW: Update & Delete View
class SubjectDetailView(APIView):
    """
    PUT /subject/<pk>/  -> Update subject
    DELETE /subject/<pk>/ -> Delete subject
    """
    parser_classes = [JSONParser]

    def get_object(self, pk):
        try:
            return Subject.objects.get(pk=pk)
        except Subject.DoesNotExist:
            return None

    def put(self, request, pk):
        subject = self.get_object(pk)
        if not subject:
            return Response(
                {"success": False, "message": "Subject not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SubjectSerializer(subject, data=request.data)
        if serializer.is_valid():
            subject = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Subject updated successfully",
                    "data": SubjectSerializer(subject).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        subject = self.get_object(pk)
        if not subject:
            return Response(
                {"success": False, "message": "Subject not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        subject.delete()
        return Response(
            {"success": True, "message": "Subject deleted successfully"},
            status=status.HTTP_200_OK,
        )