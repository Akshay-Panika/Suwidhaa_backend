from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Content
from .serializers import ContentSerializer


class ContentListAPIView(APIView):
    """GET: List all active content"""
    def get(self, request):
        contents = Content.objects.filter(is_active=True).order_by('-created_at')
        serializer = ContentSerializer(contents, many=True)
        return Response({
            "success": True,
            "count": contents.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class ContentDetailAPIView(APIView):
    """GET: Retrieve a single content item"""
    def get_object(self, pk):
        return get_object_or_404(Content, pk=pk)

    def get(self, request, pk):
        content = self.get_object(pk)
        serializer = ContentSerializer(content)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)