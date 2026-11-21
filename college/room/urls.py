from django.urls import path
from .views import CollegeRoomListView, RoomCreateView, RoomDetailView

urlpatterns = [
    path("rooms/create/", RoomCreateView.as_view(), name="room-create"),
    path(
        "colleges/<int:college_id>/rooms/",
        CollegeRoomListView.as_view(),
        name="college-rooms-list",
    ),
    path("rooms/<int:pk>/", RoomDetailView.as_view(), name="room-detail"),
]