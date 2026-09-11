from django.urls import path
from .views import (
    WebSeriesListCreateAPIView,
    WebSeriesDetailAPIView,
    SeasonListCreateAPIView,
    EpisodeListCreateAPIView,
)

urlpatterns = [
    path('webseries/list/', WebSeriesListCreateAPIView.as_view(), name='webseries-list'),
    path('webseries/create/', WebSeriesListCreateAPIView.as_view(), name='webseries-create'),
    path('webseries/<int:pk>/', WebSeriesDetailAPIView.as_view(), name='webseries-detail'),

    path('seasons/list/', SeasonListCreateAPIView.as_view(), name='season-list'),
    path('seasons/create/', SeasonListCreateAPIView.as_view(), name='season-create'),

    path('episodes/list/', EpisodeListCreateAPIView.as_view(), name='episode-list'),
    path('episodes/create/', EpisodeListCreateAPIView.as_view(), name='episode-create'),
]