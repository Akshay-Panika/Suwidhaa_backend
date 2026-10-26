from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from school.school_type.models import SchoolType
from .models import SchoolEvent
from .serializers import SchoolEventSerializer, SchoolEventCreateSerializer


# ============================================================
# 1. CREATE EVENT FOR A SPECIFIC SCHOOL
#    POST /api/v1/school/<school_id>/event/create/
# ============================================================
class SchoolEventCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, school_id):
        # Check if school exists
        school = get_object_or_404(SchoolType, pk=school_id)

        # Force the school ID into the data
        data = request.data.copy()
        data["school"] = school.id

        serializer = SchoolEventCreateSerializer(data=data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        event = serializer.save()
        return Response(
            {
                "success": True,
                "message": "Event created successfully",
                "data": SchoolEventSerializer(event).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# 2. LIST EVENTS FOR A SPECIFIC SCHOOL
#    GET /api/v1/school/<school_id>/event/list/
# ============================================================
class SchoolEventListAPIView(APIView):
    def get(self, request, school_id):
        school = get_object_or_404(SchoolType, pk=school_id)
        events = SchoolEvent.objects.filter(school=school)

        # Optional filters
        category = request.query_params.get("category")
        audience = request.query_params.get("audience")
        status_filter = request.query_params.get("status")

        if category:
            events = events.filter(category=category)
        if audience:
            events = events.filter(audience=audience)
        if status_filter:
            events = events.filter(status=status_filter)

        serializer = SchoolEventSerializer(events, many=True)
        return Response(
            {
                "success": True,
                "count": events.count(),
                "school_name": school.school_name,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# 3. RETRIEVE / UPDATE / DELETE A SPECIFIC EVENT
#    GET / PUT / DELETE /api/v1/school/<school_id>/event/<pk>/
# ============================================================
class SchoolEventDetailAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, school_id, pk):
        # Ensure the event belongs to this school
        return get_object_or_404(SchoolEvent, pk=pk, school_id=school_id)

    def get(self, request, school_id, pk):
        event = self.get_object(school_id, pk)
        return Response(
            {"success": True, "data": SchoolEventSerializer(event).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, school_id, pk):
        event = self.get_object(school_id, pk)
        serializer = SchoolEventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Event updated",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, school_id, pk):
        event = self.get_object(school_id, pk)
        event.delete()
        return Response(
            {"success": True, "message": "Event deleted"},
            status=status.HTTP_200_OK,
        )


# ============================================================
# 4. TOGGLE PIN
#    POST /api/v1/school/<school_id>/event/<pk>/toggle-pin/
# ============================================================
class SchoolEventTogglePinAPIView(APIView):
    def post(self, request, school_id, pk):
        event = get_object_or_404(SchoolEvent, pk=pk, school_id=school_id)
        event.is_pinned = not event.is_pinned
        event.save()
        return Response(
            {
                "success": True,
                "message": "Pinned" if event.is_pinned else "Unpinned",
                "data": SchoolEventSerializer(event).data,
            },
            status=status.HTTP_200_OK,
        )