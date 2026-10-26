from django.urls import path
from .views import (
    MeetingCreateView,
    MeetingListView,
    MeetingDetailView,
    MeetingDeleteView,
)

urlpatterns = [
    # Notice the <int:school_id> parameter added here
    path('<int:school_id>/meeting/create/', MeetingCreateView.as_view(), name='meeting-create'),
    path('<int:school_id>/meeting/list/', MeetingListView.as_view(), name='meeting-list'),
    path('<int:school_id>/meeting/<int:id>/', MeetingDetailView.as_view(), name='meeting-detail'),
    path('<int:school_id>/meeting/delete/<int:id>/', MeetingDeleteView.as_view(), name='meeting-delete'),
]