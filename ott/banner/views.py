from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Banner
from .serializers import BannerSerializer


class BannerListCreateAPIView(APIView):
    """GET: List all banners | POST: Upload a new banner"""

    def get(self, request):
        try:
            banners = Banner.objects.all().order_by('-created_at')
            serializer = BannerSerializer(banners, many=True)
            return Response({
                "success": True,
                "count": banners.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = BannerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Banner uploaded successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BannerDetailAPIView(APIView):
    """GET | PUT | DELETE a single banner"""

    def get_object(self, pk):
        return get_object_or_404(Banner, pk=pk)

    def get(self, request, pk):
        try:
            banner = self.get_object(pk)
            serializer = BannerSerializer(banner)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Banner.DoesNotExist:
            return Response({
                "success": False,
                "error": "Banner not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            banner = self.get_object(pk)
            serializer = BannerSerializer(banner, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Banner updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Banner.DoesNotExist:
            return Response({
                "success": False,
                "error": "Banner not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            banner = self.get_object(pk)
            banner.delete()
            return Response({
                "success": True,
                "message": "Banner deleted successfully"
            }, status=status.HTTP_200_OK)
        except Banner.DoesNotExist:
            return Response({
                "success": False,
                "error": "Banner not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)