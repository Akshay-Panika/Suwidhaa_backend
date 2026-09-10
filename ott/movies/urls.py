from django.urls import path
from .views import MovieListCreateAPIView, MovieDetailAPIView

urlpatterns = [
    # Create: POST /api/v1/ott/movies/create/
    path('movies/create/', MovieListCreateAPIView.as_view(), name='movie-create'),
    
    # List: GET /api/v1/ott/movies/list/
    path('movies/list/', MovieListCreateAPIView.as_view(), name='movie-list'),
    
    # Retrieve/Update/Delete: /api/v1/ott/movies/<movie_id>/
    path('movies/<int:pk>/', MovieDetailAPIView.as_view(), name='movie-detail'),
]