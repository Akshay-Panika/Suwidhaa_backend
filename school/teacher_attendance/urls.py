from django.urls import path
from .views import (
    TeacherCheckInView,
    TeacherCheckOutView,
    MyAttendanceHistoryView,
    TodayAttendanceView,
    AttendanceDetailView,
    AttendanceUpdateView,
    AttendanceDeleteView,
)

urlpatterns = [
    path('teacher-attendance/check-in/', TeacherCheckInView.as_view(), name='teacher-check-in'),
    path('teacher-attendance/check-out/', TeacherCheckOutView.as_view(), name='teacher-check-out'),
    path('teacher-attendance/history/', MyAttendanceHistoryView.as_view(), name='teacher-history'),
    path('teacher-attendance/today/', TodayAttendanceView.as_view(), name='teacher-today'),
    path('teacher-attendance/detail/<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),
    path('teacher-attendance/update/<int:pk>/', AttendanceUpdateView.as_view(), name='attendance-update'),
    path('teacher-attendance/delete/<int:pk>/', AttendanceDeleteView.as_view(), name='attendance-delete'),
]