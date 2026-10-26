from django.urls import path
from .views import (
    SchoolEventCreateAPIView,
    SchoolEventListAPIView,
    SchoolEventDetailAPIView,
    SchoolEventTogglePinAPIView,
)

urlpatterns = [
    # Correct paths (no "school/" at the beginning):
    path("<int:school_id>/event/create/", SchoolEventCreateAPIView.as_view()),
    path("<int:school_id>/event/list/", SchoolEventListAPIView.as_view()),
    path("<int:school_id>/event/<int:pk>/", SchoolEventDetailAPIView.as_view()),
    path("<int:school_id>/event/<int:pk>/toggle-pin/", SchoolEventTogglePinAPIView.as_view()),
]