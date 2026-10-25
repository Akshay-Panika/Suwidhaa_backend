from django.urls import path
from .views import (
    TransportCreateView,
    TransportListView,
    TransportDetailView,
    TransportStudentAddView,
    TransportStudentDeleteView,
)

urlpatterns = [
    path("transport/create/", TransportCreateView.as_view(), name="transport-create"),
    path("transport/list/", TransportListView.as_view(), name="transport-list"),
    path("transport/<int:pk>/", TransportDetailView.as_view(), name="transport-detail"),
    
    path("transport/<int:pk>/students/add/", TransportStudentAddView.as_view(), name="transport-student-add"),
    path("transport/<int:pk>/students/<int:student_id>/delete/", TransportStudentDeleteView.as_view(), name="transport-student-delete"),
]