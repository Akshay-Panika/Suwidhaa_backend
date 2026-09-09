from django.urls import path
from .views import (
    MovieCreateView,
    MovieListView,
    MovieDetailView,
)

urlpatterns = [
    path("movies/create/", MovieCreateView.as_view(), name="movie-create"),
    path("movies/list/", MovieListView.as_view(), name="movie-list"),
    path("movies/<int:pk>/", MovieDetailView.as_view(), name="movie-detail"),
]