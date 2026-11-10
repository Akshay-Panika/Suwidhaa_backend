from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from ott.content.models import Content
from ott.content.serializers import ContentSerializer
from .models import Episode
from .serializers import EpisodeSerializer, group_episodes_by_season


def _to_bool(val):
    return str(val).strip().lower() in ("true", "1", "yes", "on")


class WebseriesListAPIView(APIView):
    """
    GET /api/v1/ott/webseries/list/
    """
    BOOL_FILTERS = [
        "is_family",
        "is_recommended",
        "is_trending",
        "is_something_new",
        "is_lock",
    ]

    def get(self, request):
        try:
            qs = Content.objects.select_related("category").filter(
                category__name__iexact="Web Series"
            )

            for field in self.BOOL_FILTERS:
                val = request.query_params.get(field)
                if val is not None and val != "":
                    qs = qs.filter(**{field: _to_bool(val)})

            serializer = ContentSerializer(qs, many=True)
            return Response(
                {
                    "success": True,
                    "count": qs.count(),
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class WebseriesDetailAPIView(APIView):
    """
    GET /api/v1/ott/webseries/<id>/
    Returns web series + grouped seasons/episodes.
    """

    def get_object(self, pk):
        return get_object_or_404(
            Content.objects.prefetch_related("episodes"),
            pk=pk,
            category__name__iexact="Web Series",
        )

    def get(self, request, pk):
        try:
            content = self.get_object(pk)
            base = ContentSerializer(content).data
            # Group episodes by season_number
            base["seasons"] = group_episodes_by_season(content.episodes.all())

            return Response(
                {"success": True, "data": base},
                status=status.HTTP_200_OK,
            )
        except Content.DoesNotExist:
            return Response(
                {"success": False, "error": "Web Series not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EpisodeListCreateAPIView(APIView):
    """
    GET  /api/v1/ott/webseries/<webseries_id>/episodes/   → List episodes
    GET  ...?season_number=1                              → Filter by season
    POST /api/v1/ott/webseries/<webseries_id>/episodes/   → Create episode
         (body me season_number, episode_number, title, video_url etc.)
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, webseries_id):
        try:
            webseries = get_object_or_404(
                Content,
                pk=webseries_id,
                category__name__iexact="Web Series",
            )
            qs = Episode.objects.filter(webseries=webseries)

            # Optional season filter
            season_filter = request.query_params.get("season_number")
            if season_filter:
                qs = qs.filter(season_number=season_filter)

            serializer = EpisodeSerializer(qs, many=True)
            return Response(
                {
                    "success": True,
                    "count": qs.count(),
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, webseries_id):
        try:
            webseries = get_object_or_404(
                Content,
                pk=webseries_id,
                category__name__iexact="Web Series",
            )
            serializer = EpisodeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(webseries=webseries)
                return Response(
                    {
                        "success": True,
                        "message": "Episode created",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )