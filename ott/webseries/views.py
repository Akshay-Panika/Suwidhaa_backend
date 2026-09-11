from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import WebSeries, Season, Episode
from .serializers import (
    WebSeriesSerializer,
    SeasonSerializer,
    EpisodeSerializer,
)


# ---------------- WEB SERIES ----------------
class WebSeriesListCreateAPIView(APIView):
    def get(self, request):
        try:
            items = WebSeries.objects.all().order_by('-created_at')
            serializer = WebSeriesSerializer(items, many=True)
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
            serializer = WebSeriesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "WebSeries created successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({"success": False, "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WebSeriesDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(WebSeries, pk=pk)

    def get(self, request, pk):
        obj = self.get_object(pk)
        return Response({"success": True, "data": WebSeriesSerializer(obj).data})

    def put(self, request, pk):
        obj = self.get_object(pk)
        serializer = WebSeriesSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data})
        return Response({"success": False, "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        title = obj.title
        obj.delete()
        return Response({"success": True,
                         "message": f"WebSeries '{title}' deleted"})


# ---------------- SEASON ----------------
class SeasonListCreateAPIView(APIView):
    """GET: list seasons (optionally by webseries) | POST: create season"""

    def get(self, request):
        webseries_id = request.query_params.get('webseries')
        qs = Season.objects.all()
        if webseries_id:
            qs = qs.filter(webseries_id=webseries_id)
        return Response({
            "success": True,
            "count": qs.count(),
            "data": SeasonSerializer(qs, many=True).data
        })

    def post(self, request):
        serializer = SeasonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


# ---------------- EPISODE ----------------
class EpisodeListCreateAPIView(APIView):
    """GET: list episodes (optionally by season) | POST: create episode"""

    def get(self, request):
        season_id = request.query_params.get('season')
        qs = Episode.objects.all()
        if season_id:
            qs = qs.filter(season_id=season_id)
        return Response({
            "success": True,
            "count": qs.count(),
            "data": EpisodeSerializer(qs, many=True).data
        })

    def post(self, request):
        serializer = EpisodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)