
from django.urls import path

from .views import (
    RoomCreateView,
    RoomListView,
    RoomAllListView,
    RoomListByCollegeView,
    RoomDetailView,
)

urlpatterns = [

    path(
        'rooms/create/',
        RoomCreateView.as_view(),
        name='room-create'
    ),

    path(
        'rooms/list/',
        RoomListView.as_view(),
        name='room-list'
    ),

    path(
        'rooms/',
        RoomAllListView.as_view(),
        name='room-all-list'
    ),

    path(
        'rooms/college/<int:college_id>/',
        RoomListByCollegeView.as_view(),
        name='room-list-by-college'
    ),

    path(
        'rooms/<int:pk>/',
        RoomDetailView.as_view(),
        name='room-detail'
    ),
]
