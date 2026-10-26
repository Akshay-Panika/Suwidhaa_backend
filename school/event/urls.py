from django.urls import path
from .views import (
    SchoolEventCreateAPIView,
    SchoolEventListAPIView,
    SchoolEventDetailAPIView,
    SchoolEventTogglePinAPIView,
)

urlpatterns = [
    # Create & List
    path("school/<int:school_id>/event/create/", SchoolEventCreateAPIView.as_view(), name="event-create"),
    path("school/<int:school_id>/event/list/", SchoolEventListAPIView.as_view(), name="event-list"),
    
    # Retrieve, Update, Delete
    path("school/<int:school_id>/event/<int:pk>/", SchoolEventDetailAPIView.as_view(), name="event-detail"),
    
    # Toggle Pin
    path("school/<int:school_id>/event/<int:pk>/toggle-pin/", SchoolEventTogglePinAPIView.as_view(), name="event-toggle-pin"),
]