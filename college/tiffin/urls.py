# college/tiffins/urls.py

from django.urls import path
from .views import (
    TiffinCreateView,
    TiffinListView,        # existing (owner ke tiffins)
    TiffinAllListView,     # ✅ NAYA (sab tiffins + user-wise booking)
    TiffinDetailView,
)

urlpatterns = [
    path("tiffins/create/", TiffinCreateView.as_view(), name="tiffin-create"),
    path("tiffins/list/", TiffinListView.as_view(), name="tiffin-list"),
    path("tiffins/", TiffinAllListView.as_view(), name="tiffin-all-list"),   # ✅ NAYA
    path("tiffins/<int:pk>/", TiffinDetailView.as_view(), name="tiffin-detail"),
]