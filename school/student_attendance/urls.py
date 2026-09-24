from django.urls import path
from .views import (
    StudentAttendanceCreateView,
    StudentAttendanceListView,
    StudentAttendanceDetailView,
    StudentAttendanceDeleteView,
)

urlpatterns = [
    path(
        'student-attendance/create/',
        StudentAttendanceCreateView.as_view(),
        name='student-attendance-create'
    ),
    path(
        'student-attendance/list/',
        StudentAttendanceListView.as_view(),
        name='student-attendance-list'
    ),
    path(
        'student-attendance/list/<str:student_card_id>/',
        StudentAttendanceDetailView.as_view(),
        name='student-attendance-detail'
    ),
    path(
        'student-attendance/list/<str:student_card_id>/<str:date>/',
        StudentAttendanceDeleteView.as_view(),
        name='student-attendance-delete'
    ),
]