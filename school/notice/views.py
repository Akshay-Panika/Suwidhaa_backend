# views.py (school/notice/views.py)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from school.school_type.models import SchoolType
from .models import Notice
from .serializers import NoticeSerializer, NoticeCreateSerializer


class NoticeCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = NoticeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "Validation failed", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        notice = serializer.save()
        return Response(
            {"success": True, "message": "Notice published successfully", "data": NoticeSerializer(notice).data},
            status=status.HTTP_201_CREATED,
        )


# ✅ Naya View: Bina school ID ke saare notices fetch karne ke liye
class NoticeListAPIView(APIView):
    def get(self, request):
        notices = Notice.objects.all()

        priority = request.query_params.get("priority")
        audience = request.query_params.get("audience")
        assigned_class = request.query_params.get("class")
        is_pinned = request.query_params.get("is_pinned")

        if priority:
            notices = notices.filter(priority=priority)
        if audience:
            notices = notices.filter(audience=audience)
        if assigned_class:
            notices = notices.filter(assigned_class=assigned_class)
        if is_pinned is not None:
            notices = notices.filter(is_pinned=str(is_pinned).lower() in ("1", "true", "yes"))

        serializer = NoticeSerializer(notices, many=True)

        return Response(
            {"success": True, "count": notices.count(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class NoticeListBySchoolAPIView(APIView):
    def get(self, request, school_id):
        school = get_object_or_404(SchoolType, pk=school_id)
        notices = Notice.objects.filter(school=school)
        # ... (baki filters same rahenge)
        priority = request.query_params.get("priority")
        audience = request.query_params.get("audience")
        assigned_class = request.query_params.get("class")
        is_pinned = request.query_params.get("is_pinned")

        if priority: notices = notices.filter(priority=priority)
        if audience: notices = notices.filter(audience=audience)
        if assigned_class: notices = notices.filter(assigned_class=assigned_class)
        if is_pinned is not None: notices = notices.filter(is_pinned=str(is_pinned).lower() in ("1", "true", "yes"))

        serializer = NoticeSerializer(notices, many=True)
        return Response(
            {"success": True, "school_id": school.id, "count": notices.count(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class NoticeDetailAPIView(APIView):
    # ... (same as before)
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def get_object(self, pk): return get_object_or_404(Notice, pk=pk)
    def get(self, request, pk):
        notice = self.get_object(pk)
        return Response({"success": True, "data": NoticeSerializer(notice).data}, status=status.HTTP_200_OK)
    def put(self, request, pk):
        notice = self.get_object(pk)
        serializer = NoticeSerializer(notice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Notice updated", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request, pk): return self.put(request, pk)
    def delete(self, request, pk):
        notice = self.get_object(pk)
        notice.delete()
        return Response({"success": True, "message": "Notice deleted"}, status=status.HTTP_200_OK)


class NoticeTogglePinAPIView(APIView):
    # ... (same as before)
    def post(self, request, pk):
        notice = get_object_or_404(Notice, pk=pk)
        notice.is_pinned = not notice.is_pinned
        notice.save()
        return Response(
            {"success": True, "message": "Pinned" if notice.is_pinned else "Unpinned", "data": NoticeSerializer(notice).data},
            status=status.HTTP_200_OK,
        )