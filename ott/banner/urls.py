from django.urls import path
from .views import BannerListCreateAPIView, BannerDetailAPIView

urlpatterns = [
    path('banner/create/', BannerListCreateAPIView.as_view(), name='banner-create'),
    path('banner/list/', BannerListCreateAPIView.as_view(), name='banner-list'),
    path('banner/<int:pk>/', BannerDetailAPIView.as_view(), name='banner-detail'),
]