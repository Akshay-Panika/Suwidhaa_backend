from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from ott.content.models import Content
from ott.content.serializers import ContentSerializer
from .models import TvShowEpisode
from .serializers import (
    TvShowEpisodeSerializer,
    group_episodes_by_season,
)


def _to_bool(val):
    return str(val).strip().lower() in ("true", "1", "yes", "on")


class TvshowsListAPIView(APIView):
    """
    GET /api/v1/ott/tvshows/list/
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
                category__name__iexact="TV Shows"
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


class TvshowsDetailAPIView(APIView):
    """
    GET /api/v1/ott/tvshows/<id>/
    Returns TV show + grouped seasons/episodes.
    """

    def get_object(self, pk):
        return get_object_or_404(
            Content.objects.prefetch_related("tvshow_episodes"),
            pk=pk,
            category__name__iexact="TV Shows",
        )

    def get(self, request, pk):
        try:
            content = self.get_object(pk)
            base = ContentSerializer(content).data
            base["seasons"] = group_episodes_by_season(content.tvshow_episodes.all())

            return Response(
                {"success": True, "data": base},
                status=status.HTTP_200_OK,
            )
        except Content.DoesNotExist:
            return Response(
                {"success": False, "error": "TV Show not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class TvShowEpisodeDetailAPIView(APIView):
    """
    GET    /api/v1/ott/tvshows/<tvshow_id>/episodes/<episode_id>/
    PUT    /api/v1/ott/tvshows/<tvshow_id>/episodes/<episode_id>/
    PATCH  /api/v1/ott/tvshows/<tvshow_id>/episodes/<episode_id>/
    DELETE /api/v1/ott/tvshows/<tvshow_id>/episodes/<episode_id>/
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get_episode(self, tvshow_id, episode_id):
        return get_object_or_404(
            TvShowEpisode,
            pk=episode_id,
            tvshow_id=tvshow_id,
            tvshow__category__name__iexact="TV Shows",
        )

    def get(self, request, tvshow_id, episode_id):
        try:
            ep = self._get_episode(tvshow_id, episode_id)
            return Response(
                {"success": True, "data": TvShowEpisodeSerializer(ep).data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, tvshow_id, episode_id):
        return self._update(request, tvshow_id, episode_id, partial=False)

    def patch(self, request, tvshow_id, episode_id):
        return self._update(request, tvshow_id, episode_id, partial=True)

    def _update(self, request, tvshow_id, episode_id, partial):
        try:
            ep = self._get_episode(tvshow_id, episode_id)
            serializer = TvShowEpisodeSerializer(
                ep, data=request.data, partial=partial
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "TV Show Episode updated",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
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

    def delete(self, request, tvshow_id, episode_id):
        try:
            ep = self._get_episode(tvshow_id, episode_id)
            ep.delete()
            return Response(
                {"success": True, "message": "TV Show Episode deleted"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class TvShowEpisodeListCreateAPIView(APIView):
    """
    GET  /api/v1/ott/tvshows/<tvshow_id>/episodes/
         (optional ?season_number=1 filter)
    POST /api/v1/ott/tvshows/<tvshow_id>/episodes/
         (body me season_number, episode_number, title, video_url etc.)
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, tvshow_id):
        try:
            tvshow = get_object_or_404(
                Content,
                pk=tvshow_id,
                category__name__iexact="TV Shows",
            )
            qs = TvShowEpisode.objects.filter(tvshow=tvshow)

            season_filter = request.query_params.get("season_number")
            if season_filter:
                qs = qs.filter(season_number=season_filter)

            serializer = TvShowEpisodeSerializer(qs, many=True)
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

    def post(self, request, tvshow_id):
        try:
            tvshow = get_object_or_404(
                Content,
                pk=tvshow_id,
                category__name__iexact="TV Shows",
            )
            serializer = TvShowEpisodeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(tvshow=tvshow)
                return Response(
                    {
                        "success": True,
                        "message": "TV Show Episode created",
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