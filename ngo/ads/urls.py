from django.urls import path
from .views import AdListCreateAPIView, AdDetailAPIView

urlpatterns = [
    path("ads/create/", AdListCreateAPIView.as_view(), name="ngo-ads-create"),
    path("ads/list/", AdListCreateAPIView.as_view(), name="ngo-ads-list"),
    path("ads/<int:pk>/", AdDetailAPIView.as_view(), name="ngo-ads-detail"),
]