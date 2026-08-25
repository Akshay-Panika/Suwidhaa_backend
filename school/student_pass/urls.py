from django.urls import path
from .views import (
    StudentPassListView,
    StudentPassDetailView,
    StudentPassLoginView,
    StudentPassForgotPasswordView
)

urlpatterns = [
    path('student-pass/list/', StudentPassListView.as_view(), name='student-pass-list'),
    path('student-pass/<int:pk>/', StudentPassDetailView.as_view(), name='student-pass-detail'),
    path('student-pass/login/', StudentPassLoginView.as_view(), name='student-pass-login'),
    path('student-pass/forgot-password/', StudentPassForgotPasswordView.as_view(), name='student-pass-forgot-password'),
]