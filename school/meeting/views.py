from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Meeting
from .serializers import MeetingSerializer


# ---------------- CREATE ----------------
class MeetingCreateView(APIView):
    def post(self, request):
        serializer = MeetingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Meeting created successfully",
                    "data": serializer.data,
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


# ---------------- LIST ----------------
class MeetingListView(APIView):
    def get(self, request):
        queryset = Meeting.objects.all()

        for_meeting = request.query_params.get('for_meeting')
        class_name = request.query_params.get('class_name')
        date = request.query_params.get('date')

        if for_meeting:
            queryset = queryset.filter(for_meeting=for_meeting)
        if class_name:
            queryset = queryset.filter(class_name=class_name)
        if date:
            queryset = queryset.filter(date=date)

        serializer = MeetingSerializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "count": queryset.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ---------------- DETAIL (GET / PUT / PATCH) ----------------
class MeetingDetailView(APIView):
    def get_object(self, id):
        return get_object_or_404(Meeting, id=id)

    def get(self, request, id):
        meeting = self.get_object(id)
        serializer = MeetingSerializer(meeting)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, id):
        meeting = self.get_object(id)
        serializer = MeetingSerializer(meeting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Meeting updated successfully",
                    "data": serializer.data,
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

    def patch(self, request, id):
        meeting = self.get_object(id)
        serializer = MeetingSerializer(meeting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Meeting updated successfully",
                    "data": serializer.data,
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


# ---------------- DELETE ----------------
class MeetingDeleteView(APIView):
    def delete(self, request, id):
        meeting = get_object_or_404(Meeting, id=id)
        meeting.delete()
        return Response(
            {
                "success": True,
                "message": "Meeting deleted successfully",
            },
            status=status.HTTP_200_OK,
        )