from django.urls import path
from . import views

app_name = 'app_auth'

urlpatterns = [

    # Send SMS OTP
    path(
        'send-otp/',
        views.SendOTPView.as_view(),
        name='send-otp'
    ),

    # Verify OTP and Register/Login
    path(
        'verify-otp/',
        views.VerifyOTPView.as_view(),
        name='verify-otp'
    ),

    # Get all users
    path(
        'users/',
        views.UserListView.as_view(),
        name='user-list'
    ),

    # Delete user
    path(
        'users/<int:user_id>/delete/',
        views.UserDeleteView.as_view(),
        name='user-delete'
    ),

]