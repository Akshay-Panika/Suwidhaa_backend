from django.urls import path
from .views import (
    TvshowsListAPIView,
    TvshowsDetailAPIView,
    TvShowEpisodeListCreateAPIView,
)

urlpatterns = [
    path("tvshows/list/", TvshowsListAPIView.as_view(), name="tvshows-list"),
    path("tvshows/<int:pk>/", TvshowsDetailAPIView.as_view(), name="tvshows-detail"),
    path(
        "tvshows/<int:tvshow_id>/episodes/",
        TvShowEpisodeListCreateAPIView.as_view(),
        name="tvshows-episodes",
    ),
]