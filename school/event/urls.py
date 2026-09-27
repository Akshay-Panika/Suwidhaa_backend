from django.urls import path
from .views import (
    SchoolEventCreateAPIView,
    SchoolEventListAPIView,
    SchoolEventDetailAPIView,
    SchoolEventTogglePinAPIView,
)

urlpatterns = [
    path("event/create/", SchoolEventCreateAPIView.as_view(), name="event-create"),
    path("event/list/", SchoolEventListAPIView.as_view(), name="event-list"),
    path("event/<int:pk>/", SchoolEventDetailAPIView.as_view(), name="event-detail"),
    path(
        "event/<int:pk>/toggle-pin/",
        SchoolEventTogglePinAPIView.as_view(),
        name="event-toggle-pin",
    ),
]