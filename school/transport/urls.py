# school/transport/urls.py
from django.urls import path
from .views import (
    TransportCreateView,
    TransportListView,
    TransportDetailView,
    TransportStudentManagementView,
)

urlpatterns = [
    # Transport CRUD
    path("transport/create/", TransportCreateView.as_view(), name="transport-create"),
    path("transport/list/", TransportListView.as_view(), name="transport-list"),
    path("transport/<int:pk>/", TransportDetailView.as_view(), name="transport-detail"),
    
    # Student Management (Add/Update/Delete students within transport)
    path("transport/<int:pk>/students/", TransportStudentManagementView.as_view(), name="transport-students"),
]