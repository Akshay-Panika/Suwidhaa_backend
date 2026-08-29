from django.urls import path
from .views import StudentPassListView, StudentPassDetailView, StudentPassLoginView, StudentPassForgotPasswordView

urlpatterns = [
    path('student-pass/list/', StudentPassListView.as_view()),
    path('student-pass/<int:pk>/', StudentPassDetailView.as_view()),
    path('student-pass/login/', StudentPassLoginView.as_view()),
    path('student-pass/forgot-password/', StudentPassForgotPasswordView.as_view()),
]