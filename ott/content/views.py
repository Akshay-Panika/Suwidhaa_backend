from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Content
from .serializers import ContentSerializer


class ContentListAPIView(APIView):
    """GET: List all content"""
    def get(self, request):
        try:
            contents = Content.objects.all().order_by('-created_at')
            serializer = ContentSerializer(contents, many=True)
            return Response({
                "success": True,
                "count": contents.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContentDetailAPIView(APIView):
    """GET: Retrieve a single content item"""
    def get(self, request, pk):
        try:
            content = get_object_or_404(Content, pk=pk)
            serializer = ContentSerializer(content)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Content.DoesNotExist:
            return Response({
                "success": False,
                "error": "Content not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)