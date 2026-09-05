from django.urls import path
from . import views

urlpatterns = [
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/users/', views.UserListView.as_view(), name='user-list'),
    path('api/users/<int:user_id>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
]