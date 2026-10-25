from django.urls import path
from .views import (
    TransportCreateView,
    TransportListView,
    TransportBySchoolView,  # ✅ Import karein
    TransportDetailView,
    TransportStudentAddView,
    TransportStudentDeleteView,
)

urlpatterns = [
    path("transport/create/", TransportCreateView.as_view(), name="transport-create"),
    
    # ✅ ALL Transports
    path("transport/list/", TransportListView.as_view(), name="transport-list"),
    
    # ✅ School wise Transports
    path("transport/list/school/<int:school_id>/", TransportBySchoolView.as_view(), name="transport-by-school"),
    
    path("transport/<int:pk>/", TransportDetailView.as_view(), name="transport-detail"),
    
    path("transport/<int:pk>/students/add/", TransportStudentAddView.as_view(), name="transport-student-add"),
    path("transport/<int:pk>/students/<int:student_id>/delete/", TransportStudentDeleteView.as_view(), name="transport-student-delete"),
]