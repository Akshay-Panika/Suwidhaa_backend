from django.urls import path
from .views import (
    TeacherPassListView,
    TeacherPassDetailView,
    TeacherPassLoginView,
    TeacherRequestForgotPasswordOtpView,
    TeacherVerifyOtpAndResetPasswordView,
    TeacherPassLogoutView,
)

urlpatterns = [
    path("teacher-pass/list/", TeacherPassListView.as_view()),
    path("teacher-pass/<int:pk>/", TeacherPassDetailView.as_view()),
    path("teacher-pass/login/", TeacherPassLoginView.as_view()),

    # Forgot Password (OTP flow)
    path(
        "teacher-pass/forgot-password/request-otp/",
        TeacherRequestForgotPasswordOtpView.as_view(),
    ),
    path(
        "teacher-pass/forgot-password/verify-and-reset/",
        TeacherVerifyOtpAndResetPasswordView.as_view(),
    ),

    # Logout
    path("teacher-pass/logout/", TeacherPassLogoutView.as_view()),
]