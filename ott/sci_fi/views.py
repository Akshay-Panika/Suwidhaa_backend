from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import SciFi
from .serializers import SciFiSerializer


class SciFiListCreateAPIView(APIView):
    """GET: List all sci-fi | POST: Create a new sci-fi"""

    def get(self, request):
        try:
            items = SciFi.objects.all().order_by('-created_at')
            serializer = SciFiSerializer(items, many=True)
            return Response({
                "success": True,
                "count": items.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = SciFiSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Sci-Fi created successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SciFiDetailAPIView(APIView):
    """GET | PUT | DELETE a single sci-fi"""

    def get_object(self, pk):
        return get_object_or_404(SciFi, pk=pk)

    def get(self, request, pk):
        try:
            item = self.get_object(pk)
            serializer = SciFiSerializer(item)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except SciFi.DoesNotExist:
            return Response({"success": False, "error": "Sci-Fi not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            item = self.get_object(pk)
            serializer = SciFiSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Sci-Fi updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except SciFi.DoesNotExist:
            return Response({"success": False, "error": "Sci-Fi not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            item = self.get_object(pk)
            title = item.title
            item.delete()
            return Response({
                "success": True,
                "message": f"Sci-Fi '{title}' deleted successfully"
            }, status=status.HTTP_200_OK)
        except SciFi.DoesNotExist:
            return Response({"success": False, "error": "Sci-Fi not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)