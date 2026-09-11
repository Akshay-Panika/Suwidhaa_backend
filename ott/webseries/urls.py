from django.urls import path
from .views import (
    WebseriesListCreateAPIView,
    WebseriesDetailAPIView,
    SeasonCreateAPIView,
    EpisodeCreateAPIView,
)

urlpatterns = [
    # Webseries
    path('webseries/create/', WebseriesListCreateAPIView.as_view(), name='webseries-create'),
    path('webseries/list/', WebseriesListCreateAPIView.as_view(), name='webseries-list'),
    path('webseries/<int:pk>/', WebseriesDetailAPIView.as_view(), name='webseries-detail'),

    # Season (add to existing webseries)
    path('webseries/seasons/create/', SeasonCreateAPIView.as_view(), name='season-create'),

    # Episode (add video to a season)
    path('webseries/episodes/create/', EpisodeCreateAPIView.as_view(), name='episode-create'),
]