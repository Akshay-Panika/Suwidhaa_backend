from django.urls import path
from .views import (
    WebseriesListAPIView,
    WebseriesDetailAPIView,
    EpisodeListCreateAPIView,
    EpisodeDetailAPIView,   # ✅ new import
)

urlpatterns = [
    path("webseries/list/", WebseriesListAPIView.as_view(), name="webseries-list"),
    path("webseries/<int:pk>/", WebseriesDetailAPIView.as_view(), name="webseries-detail"),
    path(
        "webseries/<int:webseries_id>/episodes/",
        EpisodeListCreateAPIView.as_view(),
        name="webseries-episodes",
    ),
    # ✅ New
    path(
        "webseries/<int:webseries_id>/episodes/<int:episode_id>/",
        EpisodeDetailAPIView.as_view(),
        name="webseries-episode-detail",
    ),
]