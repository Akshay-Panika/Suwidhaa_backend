from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from .models import Notice
from .serializers import NoticeSerializer, NoticeCreateSerializer


# ============================================================
# 1. CREATE NOTICE
#    POST /api/v1/school/notice/create/
#    Content-Type: multipart/form-data  (when file attached)
#    Content-Type: application/json     (when no file)
# ============================================================
class NoticeCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = NoticeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        notice = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Notice published successfully",
                "data": NoticeSerializer(notice).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# 2. LIST ALL NOTICES
#    GET /api/v1/school/notice/list/
# ============================================================
class NoticeListAPIView(APIView):
    def get(self, request):
        notices = Notice.objects.all()

        priority = request.query_params.get("priority")
        audience = request.query_params.get("audience")
        assigned_class = request.query_params.get("class")

        if priority:
            notices = notices.filter(priority=priority)
        if audience:
            notices = notices.filter(audience=audience)
        if assigned_class:
            notices = notices.filter(assigned_class=assigned_class)

        serializer = NoticeSerializer(notices, many=True)
        return Response(
            {
                "success": True,
                "count": notices.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# 3. RETRIEVE / UPDATE / DELETE
# ============================================================
class NoticeDetailAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        return get_object_or_404(Notice, pk=pk)

    def get(self, request, pk):
        notice = self.get_object(pk)
        return Response(
            {"success": True, "data": NoticeSerializer(notice).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        notice = self.get_object(pk)
        serializer = NoticeSerializer(notice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Notice updated",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        notice = self.get_object(pk)
        notice.delete()
        return Response(
            {"success": True, "message": "Notice deleted"},
            status=status.HTTP_200_OK,
        )


# ============================================================
# 4. PIN / UNPIN NOTICE
#    POST /api/v1/school/notice/<id>/toggle-pin/
# ============================================================
class NoticeTogglePinAPIView(APIView):
    def post(self, request, pk):
        notice = get_object_or_404(Notice, pk=pk)
        notice.is_pinned = not notice.is_pinned
        notice.save()
        return Response(
            {
                "success": True,
                "message": "Pinned" if notice.is_pinned else "Unpinned",
                "data": NoticeSerializer(notice).data,
            },
            status=status.HTTP_200_OK,
        )