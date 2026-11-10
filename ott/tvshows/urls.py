from django.urls import path
from .views import (
    TvshowsListAPIView,
    TvshowsDetailAPIView,
    TvShowEpisodeListCreateAPIView,
    TvShowEpisodeDetailAPIView,   # ✅ new import
)

urlpatterns = [
    path("tvshows/list/", TvshowsListAPIView.as_view(), name="tvshows-list"),
    path("tvshows/<int:pk>/", TvshowsDetailAPIView.as_view(), name="tvshows-detail"),
    path(
        "tvshows/<int:tvshow_id>/episodes/",
        TvShowEpisodeListCreateAPIView.as_view(),
        name="tvshows-episodes",
    ),
    # ✅ New
    path(
        "tvshows/<int:tvshow_id>/episodes/<int:episode_id>/",
        TvShowEpisodeDetailAPIView.as_view(),
        name="tvshows-episode-detail",
    ),
]