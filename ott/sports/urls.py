from django.urls import path
from .views import SportListCreateAPIView, SportDetailAPIView

urlpatterns = [
    path('sports/create/', SportListCreateAPIView.as_view(), name='sport-create'),
    path('sports/list/', SportListCreateAPIView.as_view(), name='sport-list'),
    path('sports/<int:pk>/', SportDetailAPIView.as_view(), name='sport-detail'),
]