from django.urls import path
from .views import (
    TeacherAttendanceListView,
    TeacherCheckInView,
    TeacherCheckOutView,
    TeacherAttendanceHistoryView,
    AttendanceUpdateView,
    AttendanceDeleteView,
)

urlpatterns = [
    path('teacher-attendance/list/', TeacherAttendanceListView.as_view(), name='teacher-attendance-list'),
    path('teacher-attendance/check-in/', TeacherCheckInView.as_view(), name='teacher-check-in'),
    path('teacher-attendance/check-out/', TeacherCheckOutView.as_view(), name='teacher-check-out'),
    path('teacher-attendance/history/', TeacherAttendanceHistoryView.as_view(), name='teacher-history'),
    path('teacher-attendance/update/', AttendanceUpdateView.as_view(), name='attendance-update'),
    path('teacher-attendance/delete/<int:pk>/', AttendanceDeleteView.as_view(), name='attendance-delete'),
]