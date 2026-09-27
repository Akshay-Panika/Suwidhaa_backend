from django.urls import path
from .views import (
    LibraryCreateView,
    LibraryListView,
    LibraryDetailView,
)

urlpatterns = [
    path("library/create/", LibraryCreateView.as_view(), name="library-create"),
    path("library/list/", LibraryListView.as_view(), name="library-list"),
    path("library/<int:pk>/", LibraryDetailView.as_view(), name="library-detail"),
]