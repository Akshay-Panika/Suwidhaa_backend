from django.urls import path
from .views import (
    TeacherCreateView,
    TeacherListView,
    TeacherDetailView,
)

urlpatterns = [
    path("teacher/create/", TeacherCreateView.as_view(), name="teacher-create"),
    path("teacher/list/", TeacherListView.as_view(), name="teacher-list"),
    path("teacher/<int:pk>/", TeacherDetailView.as_view(), name="teacher-detail"),
]