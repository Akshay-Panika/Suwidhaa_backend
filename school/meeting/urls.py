from django.urls import path
from .views import (
    MeetingCreateView,
    MeetingListView,
    MeetingDetailView,
    MeetingDeleteView,
)

urlpatterns = [
    path('meeting/create/', MeetingCreateView.as_view(), name='meeting-create'),
    path('meeting/list/', MeetingListView.as_view(), name='meeting-list'),
    path('meeting/<int:id>/', MeetingDetailView.as_view(), name='meeting-detail'),
    path('meeting/delete/<int:id>/', MeetingDeleteView.as_view(), name='meeting-delete'),
]