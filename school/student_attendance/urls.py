from django.urls import path
from .views import (
    StudentAttendanceCreateView,
    StudentAttendanceCreateOrUpdateView,  # ✅ Naya
    StudentAttendanceListView,
    StudentAttendanceDetailView,
    StudentAttendanceDeleteView,
)

urlpatterns = [
    # ✅ Naya endpoint: single student update/create
    path(
        'student-attendance/update/',
        StudentAttendanceCreateOrUpdateView.as_view(),
        name='student-attendance-update'
    ),

    # Bulk create (purana)
    path(
        'student-attendance/create/',
        StudentAttendanceCreateView.as_view(),
        name='student-attendance-create'
    ),

    # List, Detail, Delete
    path(
        'student-attendance/list/',
        StudentAttendanceListView.as_view(),
        name='student-attendance-list'
    ),
    path(
        'student-attendance/list/<int:student_id>/',
        StudentAttendanceDetailView.as_view(),
        name='student-attendance-detail'
    ),
    path(
        'student-attendance/list/<int:student_id>/<str:date>/',
        StudentAttendanceDeleteView.as_view(),
        name='student-attendance-delete'
    ),
]