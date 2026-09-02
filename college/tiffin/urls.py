from django.urls import path
from .views import (
    TiffinCreateView,
    TiffinListView,
    TiffinDetailView,
)

urlpatterns = [
    path("tiffins/create/", TiffinCreateView.as_view(), name="tiffin-create"),
    path("tiffins/list/", TiffinListView.as_view(), name="tiffin-list"),
    path("tiffins/<int:pk>/", TiffinDetailView.as_view(), name="tiffin-detail"),
]