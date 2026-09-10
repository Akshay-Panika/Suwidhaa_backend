from django.urls import path
from .views import MovieListCreateAPIView, MovieDetailAPIView

urlpatterns = [
    path('movies/create/', MovieListCreateAPIView.as_view(), name='movie-create'),
    path('movies/list/', MovieListCreateAPIView.as_view(), name='movie-list'),
    path('movies/<int:pk>/', MovieDetailAPIView.as_view(), name='movie-detail'),
]