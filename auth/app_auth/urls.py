from django.urls import path
from . import views

app_name = 'app_auth'

urlpatterns = [
    path('send-otp/', views.SendOTPView.as_view(), name='send-otp'),

    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),

    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('users/', views.UserListView.as_view(), name='user-list'),

    path(
        'users/<int:user_id>/delete/',
        views.UserDeleteView.as_view(),
        name='user-delete'
    ),
]