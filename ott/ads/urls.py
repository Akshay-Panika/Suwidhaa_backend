from django.urls import path
from .views import OttAdsListCreateAPIView, OttAdsDetailAPIView

urlpatterns = [
    path("ads/create/", OttAdsListCreateAPIView.as_view(), name="ott-ads-create"),
    path("ads/list/", OttAdsListCreateAPIView.as_view(), name="ott-ads-list"),
    path("ads/<int:pk>/", OttAdsDetailAPIView.as_view(), name="ott-ads-detail"),
]