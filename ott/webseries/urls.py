from django.urls import path
from .views import (
    WebseriesListCreateAPIView,
    WebseriesDetailAPIView,
    SeasonCreateAPIView,
    SeasonDetailAPIView,
    EpisodeCreateAPIView,
    EpisodeDetailAPIView,
)

urlpatterns = [
    # Webseries
    path('webseries/create/', WebseriesListCreateAPIView.as_view(), name='webseries-create'),
    path('webseries/list/', WebseriesListCreateAPIView.as_view(), name='webseries-list'),
    path('webseries/<int:pk>/', WebseriesDetailAPIView.as_view(), name='webseries-detail'),

    # Season
    path('webseries/seasons/create/', SeasonCreateAPIView.as_view(), name='season-create'),
    path('webseries/seasons/<int:pk>/', SeasonDetailAPIView.as_view(), name='season-detail'),

    # Episode
    path('webseries/episodes/create/', EpisodeCreateAPIView.as_view(), name='episode-create'),
    path('webseries/episodes/<int:pk>/', EpisodeDetailAPIView.as_view(), name='episode-detail'),
]