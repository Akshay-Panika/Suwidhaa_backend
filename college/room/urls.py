from django.urls import path
from .views import (
    RoomCreateView,
    RoomListView,
    RoomDetailView,
)

urlpatterns = [
    path("rooms/create/", RoomCreateView.as_view(), name="room-create"),
    path("rooms/list/", RoomListView.as_view(), name="room-list"),
    path("rooms/<int:pk>/", RoomDetailView.as_view(), name="room-detail"),
]