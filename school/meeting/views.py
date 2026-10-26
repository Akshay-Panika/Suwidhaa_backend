from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from school.school_type.models import SchoolType
from .models import Meeting
from .serializers import MeetingSerializer


# ---------------- CREATE (School Specific) ----------------
class MeetingCreateView(APIView):
    def post(self, request, school_id):
        school = get_object_or_404(SchoolType, pk=school_id)
        
        # Force the school ID into the data
        data = request.data.copy()
        data['school'] = school.id

        serializer = MeetingSerializer(data=data)
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


# ---------------- LIST (School Specific) ----------------
class MeetingListView(APIView):
    def get(self, request, school_id):
        school = get_object_or_404(SchoolType, pk=school_id)
        queryset = Meeting.objects.filter(school=school)

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
                "school_name": school.school_name,
                "count": queryset.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ---------------- DETAIL (GET / PUT / PATCH) ----------------
class MeetingDetailView(APIView):
    def get_object(self, school_id, id):
        # Ensure the meeting belongs to this school
        return get_object_or_404(Meeting, id=id, school_id=school_id)

    def get(self, request, school_id, id):
        meeting = self.get_object(school_id, id)
        serializer = MeetingSerializer(meeting)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, school_id, id):
        meeting = self.get_object(school_id, id)
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

    def patch(self, request, school_id, id):
        meeting = self.get_object(school_id, id)
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
    def delete(self, request, school_id, id):
        meeting = get_object_or_404(Meeting, id=id, school_id=school_id)
        meeting.delete()
        return Response(
            {
                "success": True,
                "message": "Meeting deleted successfully",
            },
            status=status.HTTP_200_OK,
        )