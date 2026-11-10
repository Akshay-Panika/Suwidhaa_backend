from django.urls import path
from .views import (
    WebseriesListAPIView,
    WebseriesDetailAPIView,
    EpisodeListCreateAPIView,
)

urlpatterns = [
    path("webseries/list/", WebseriesListAPIView.as_view(), name="webseries-list"),
    path("webseries/<int:pk>/", WebseriesDetailAPIView.as_view(), name="webseries-detail"),
    path(
        "webseries/<int:webseries_id>/episodes/",
        EpisodeListCreateAPIView.as_view(),
        name="webseries-episodes",
    ),
]