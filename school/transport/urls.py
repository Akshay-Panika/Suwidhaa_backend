# school/transport/urls.py
from django.urls import path
from .views import (
    TransportCreateView,
    TransportListView,
    TransportDetailView,
    TransportStudentAddView,
    TransportStudentBulkAddView,
    TransportStudentUpdateView,
    TransportStudentDeleteView,
    TransportStudentListView,
)

urlpatterns = [
    # Transport CRUD
    path("transport/create/", TransportCreateView.as_view(), name="transport-create"),
    path("transport/list/", TransportListView.as_view(), name="transport-list"),
    path("transport/<int:pk>/", TransportDetailView.as_view(), name="transport-detail"),
    
    # Student Management
    path("transport/<int:pk>/students/", TransportStudentListView.as_view(), name="transport-students-list"),
    path("transport/<int:pk>/students/add/", TransportStudentAddView.as_view(), name="transport-student-add"),
    path("transport/<int:pk>/students/bulk-add/", TransportStudentBulkAddView.as_view(), name="transport-student-bulk-add"),
    path("transport/<int:pk>/students/<str:student_id>/", TransportStudentUpdateView.as_view(), name="transport-student-update"),
    path("transport/<int:pk>/students/<str:student_id>/delete/", TransportStudentDeleteView.as_view(), name="transport-student-delete"),
]