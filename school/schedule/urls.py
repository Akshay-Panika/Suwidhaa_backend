from django.urls import path
from .views import (
    ScheduleCreateView,
    ScheduleListView,
    ScheduleDetailView,
)

urlpatterns = [
    path("schedule/create/", ScheduleCreateView.as_view()),
    path("schedule/list/", ScheduleListView.as_view()),
    path("schedule/<int:pk>/", ScheduleDetailView.as_view()),
]