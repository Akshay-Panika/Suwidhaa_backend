from django.urls import path
from . import views

app_name = 'app_auth'

urlpatterns = [
    # User registration with OTP
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    
    # Verify OTP
    path('verify-otp/', views.OTPVerifyView.as_view(), name='verify-otp'),
    
    # Resend OTP
    path('resend-otp/', views.OTPResendView.as_view(), name='resend-otp'),
    
    # User login
    path('login/', views.UserLoginView.as_view(), name='login'),
    
    # User profile (get/update)
    path('profile/', views.UserProfileView.as_view(), name='profile'),
]