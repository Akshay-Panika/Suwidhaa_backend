from django.urls import path
from .views import (
    StudentCreateView,
    StudentListView,
    StudentDetailView,
)

urlpatterns = [
    path("student/create/", StudentCreateView.as_view()),
    path("student/list/", StudentListView.as_view()),
    path("student/<int:pk>/", StudentDetailView.as_view()),
]