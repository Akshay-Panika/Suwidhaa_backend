# college/rooms/urls.py

from django.urls import path
from .views import (
    RoomCreateView,
    RoomListView,          # existing (owner ke rooms)
    RoomAllListView,       # ✅ NAYA (sab rooms + user-wise booking)
    RoomDetailView,
)

urlpatterns = [
    path("rooms/create/", RoomCreateView.as_view(), name="room-create"),
    path("rooms/list/", RoomListView.as_view(), name="room-list"),
    path("rooms/", RoomAllListView.as_view(), name="room-all-list"),   # ✅ NAYA
    path("rooms/<int:pk>/", RoomDetailView.as_view(), name="room-detail"),
]