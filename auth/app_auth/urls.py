from django.urls import path
from . import views

app_name = 'app_auth'

urlpatterns = [
    path('auth/', views.RegisterView.as_view(), name='auth'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
]