from django.urls import path
from .views import ReelListCreateAPIView, ReelDetailAPIView

urlpatterns = [
    path('reels/create/', ReelListCreateAPIView.as_view(), name='reel-list-create'),
    path('reels/<int:pk>/', ReelDetailAPIView.as_view(), name='reel-detail'),
]