# school/teacher_attendance/urls.py
from django.urls import path
from .views import (
    TeacherAttendanceCreateView,
    TeacherAttendanceListView,
    TeacherAttendanceDetailView,
    TeacherAttendanceDeleteView,
    TeacherCheckInView,
    TeacherCheckOutView,
    TodayAttendanceView,
    MyAttendanceHistoryView,
)

urlpatterns = [
    path(
        'teacher-attendance/create/',
        TeacherAttendanceCreateView.as_view(),
        name='teacher-attendance-create'
    ),
    path(
        'teacher-attendance/list/',
        TeacherAttendanceListView.as_view(),
        name='teacher-attendance-list'
    ),
    path(
        'teacher-attendance/list/<int:teacher_id>/',
        TeacherAttendanceDetailView.as_view(),
        name='teacher-attendance-detail'
    ),
    path(
        'teacher-attendance/list/<int:teacher_id>/<str:date>/',
        TeacherAttendanceDeleteView.as_view(),
        name='teacher-attendance-delete'
    ),

    # Check-in/out rahenge
    path('teacher-attendance/check-in/', TeacherCheckInView.as_view(), name='teacher-check-in'),
    path('teacher-attendance/check-out/', TeacherCheckOutView.as_view(), name='teacher-check-out'),
    path('teacher-attendance/today/', TodayAttendanceView.as_view(), name='teacher-today'),
    path('teacher-attendance/history/', MyAttendanceHistoryView.as_view(), name='teacher-history'),
]