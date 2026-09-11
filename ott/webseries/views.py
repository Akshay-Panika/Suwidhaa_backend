from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Webseries, Season, Episode
from .serializers import (
    WebseriesSerializer,
    SeasonSerializer,
    EpisodeSerializer,
)


# =========================================================
# WEBSERIES
# =========================================================
class WebseriesListCreateAPIView(APIView):
    """GET: list all webseries (with seasons+episodes) | POST: create webseries"""

    def get(self, request):
        try:
            items = Webseries.objects.all().order_by('-created_at')
            serializer = WebseriesSerializer(items, many=True)
            return Response({
                "success": True,
                "count": items.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = WebseriesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Webseries created successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({"success": False, "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WebseriesDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Webseries, pk=pk)

    def get(self, request, pk):
        try:
            obj = self.get_object(pk)
            return Response({
                "success": True,
                "data": WebseriesSerializer(obj).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            obj = self.get_object(pk)
            serializer = WebseriesSerializer(obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"success": True, "data": serializer.data},
                                status=status.HTTP_200_OK)
            return Response({"success": False, "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            obj = self.get_object(pk)
            title = obj.title
            obj.delete()
            return Response({
                "success": True,
                "message": f"Webseries '{title}' deleted successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =========================================================
# SEASON (add to existing webseries)
# =========================================================
class SeasonCreateAPIView(APIView):
    """POST: add a new season to a webseries
    Body: { "webseries": <id>, "season_number": 1, "title": "...", ... }"""

    def post(self, request):
        try:
            serializer = SeasonSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Season added successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({"success": False, "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =========================================================
# EPISODE (add video to a season)
# =========================================================
class EpisodeCreateAPIView(APIView):
    """POST: add a new episode (with video_url) to a season
    Body: { "season": <id>, "episode_number": 1, "title": "...",
            "video_url": "...", "duration": "45m", ... }"""

    def post(self, request):
        try:
            serializer = EpisodeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Episode added successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({"success": False, "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)