from django.urls import path
from .views import (
    HomeworkCreateView,
    HomeworkListView,
    HomeworkDetailView
)

urlpatterns = [
    path("homework/create/", HomeworkCreateView.as_view(), name="homework-create"),
    path("homework/list/", HomeworkListView.as_view(), name="homework-list"),
    path("homework/<int:pk>/", HomeworkDetailView.as_view(), name="homework-detail"),
]