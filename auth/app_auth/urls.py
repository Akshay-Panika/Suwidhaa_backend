from django.urls import path
from . import views

app_name = 'app_auth'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
]