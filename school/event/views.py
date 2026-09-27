from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from .models import SchoolEvent
from .serializers import SchoolEventSerializer, SchoolEventCreateSerializer


# ============================================================
# 1. CREATE EVENT
#    POST /api/v1/school/event/create/
# ============================================================
class SchoolEventCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = SchoolEventCreateSerializer(data=request.data)
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
                "message": "Event hosted successfully",
                "data": SchoolEventSerializer(event).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# 2. LIST EVENTS
#    GET /api/v1/school/event/list/
# ============================================================
class SchoolEventListAPIView(APIView):
    def get(self, request):
        events = SchoolEvent.objects.all()

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
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# 3. RETRIEVE / UPDATE / DELETE
#    GET / PUT / DELETE /api/v1/school/event/<id>/
# ============================================================
class SchoolEventDetailAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        return get_object_or_404(SchoolEvent, pk=pk)

    def get(self, request, pk):
        event = self.get_object(pk)
        return Response(
            {"success": True, "data": SchoolEventSerializer(event).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        event = self.get_object(pk)
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

    def delete(self, request, pk):
        event = self.get_object(pk)
        event.delete()
        return Response(
            {"success": True, "message": "Event deleted"},
            status=status.HTTP_200_OK,
        )


# ============================================================
# 4. TOGGLE PIN
#    POST /api/v1/school/event/<id>/toggle-pin/
# ============================================================
class SchoolEventTogglePinAPIView(APIView):
    def post(self, request, pk):
        event = get_object_or_404(SchoolEvent, pk=pk)
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