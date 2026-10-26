from django.urls import path
from .views import (
    SchoolEventCreateAPIView,
    SchoolEventListAPIView,
    SchoolEventDetailAPIView,
    SchoolEventTogglePinAPIView,
)

urlpatterns = [
    # Create & List
    path("<int:school_id>/event/create/", SchoolEventCreateAPIView.as_view(), name="event-create"),
    path("<int:school_id>/event/list/", SchoolEventListAPIView.as_view(), name="event-list"),
    
    # Retrieve, Update, Delete
    path("<int:school_id>/event/<int:pk>/", SchoolEventDetailAPIView.as_view(), name="event-detail"),
    
    # Toggle Pin
    path("<int:school_id>/event/<int:pk>/toggle-pin/", SchoolEventTogglePinAPIView.as_view(), name="event-toggle-pin"),
]