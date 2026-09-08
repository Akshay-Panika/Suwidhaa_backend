from django.urls import path
from . import views

app_name = 'app_auth'

urlpatterns = [
    # Single endpoint for both registration and login
    path('auth/', views.RegisterView.as_view(), name='auth'),
    
    # List all users
    path('users/', views.UserListView.as_view(), name='user-list'),
    
    # Delete user by ID
    path('users/<int:user_id>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
]