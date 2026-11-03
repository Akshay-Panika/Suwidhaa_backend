from django.urls import path
from .views import (
    StudentPassListView, 
    StudentPassDetailView, 
    StudentPassLoginView, 
    RequestForgotPasswordOtpView,
    VerifyOtpAndResetPasswordView,
    StudentPassLogoutView
)

urlpatterns = [
    path('student-pass/list/', StudentPassListView.as_view()),
    path('student-pass/<int:pk>/', StudentPassDetailView.as_view()),
    path('student-pass/login/', StudentPassLoginView.as_view()),
    
    # Forgot Password Flow
    path('student-pass/forgot-password/request-otp/', RequestForgotPasswordOtpView.as_view()),
    path('student-pass/forgot-password/verify-and-reset/', VerifyOtpAndResetPasswordView.as_view()),
    
    # Logout API
    path('student-pass/logout/', StudentPassLogoutView.as_view()),
]