from django.urls import path
from .views import SciFiListCreateAPIView, SciFiDetailAPIView

urlpatterns = [
    path('sci-fi/create/', SciFiListCreateAPIView.as_view(), name='scifi-create'),
    path('sci-fi/list/', SciFiListCreateAPIView.as_view(), name='scifi-list'),
    path('sci-fi/<int:pk>/', SciFiDetailAPIView.as_view(), name='scifi-detail'),
]