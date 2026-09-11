from django.urls import path
from .views import ReelListAPIView, ReelCreateAPIView

urlpatterns = [
    path('reels/list/', ReelListAPIView.as_view(), name='reel-list'),
    path('reels/create/', ReelCreateAPIView.as_view(), name='reel-create'),
]