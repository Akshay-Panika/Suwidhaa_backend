from django.urls import path
from .views import (
    TeacherPassListView,
    TeacherPassDetailView,
    TeacherPassLoginView,
    TeacherPassForgotPasswordView
)

urlpatterns = [
    path('teacher-pass/list/', TeacherPassListView.as_view()),
    path('teacher-pass/<int:pk>/', TeacherPassDetailView.as_view()),
    path('teacher-pass/login/', TeacherPassLoginView.as_view()),
    path('teacher-pass/forgot-password/', TeacherPassForgotPasswordView.as_view()),
]