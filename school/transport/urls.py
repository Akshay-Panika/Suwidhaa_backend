# school/transport/urls.py
from django.urls import path
from .views import (
    TransportCreateView,
    TransportListView,
    TransportDetailView,
)

urlpatterns = [
    # Transport CRUD (No students management)
    path("transport/create/", TransportCreateView.as_view(), name="transport-create"),
    path("transport/list/", TransportListView.as_view(), name="transport-list"),
    path("transport/<int:pk>/", TransportDetailView.as_view(), name="transport-detail"),
]