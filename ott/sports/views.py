from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Sport
from .serializers import SportSerializer


class SportListCreateAPIView(APIView):
    """GET: List all sports | POST: Create a new sport"""

    def get(self, request):
        try:
            sports = Sport.objects.all().order_by('-created_at')
            serializer = SportSerializer(sports, many=True)
            return Response({
                "success": True,
                "count": sports.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = SportSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Sport created successfully",
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


class SportDetailAPIView(APIView):
    """GET | PUT | DELETE a single sport"""

    def get_object(self, pk):
        return get_object_or_404(Sport, pk=pk)

    def get(self, request, pk):
        try:
            sport = self.get_object(pk)
            serializer = SportSerializer(sport)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Sport.DoesNotExist:
            return Response({"success": False, "error": "Sport not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            sport = self.get_object(pk)
            serializer = SportSerializer(sport, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Sport updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Sport.DoesNotExist:
            return Response({"success": False, "error": "Sport not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            sport = self.get_object(pk)
            title = sport.title
            sport.delete()
            return Response({
                "success": True,
                "message": f"Sport '{title}' deleted successfully"
            }, status=status.HTTP_200_OK)
        except Sport.DoesNotExist:
            return Response({"success": False, "error": "Sport not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)