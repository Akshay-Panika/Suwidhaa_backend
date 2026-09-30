from django.urls import path
from .views import (
    HomeworkCreateView,
    HomeworkListView,
    HomeworkByTeacherView,  
    HomeworkDetailView
)

urlpatterns = [
    path("homework/create/", HomeworkCreateView.as_view(), name="homework-create"),
    path("homework/list/", HomeworkListView.as_view(), name="homework-list"),
    path("homework/list/<str:teacher_id>/", HomeworkByTeacherView.as_view(), name="homework-list-by-teacher"),
    path("homework/<int:pk>/", HomeworkDetailView.as_view(), name="homework-detail"),
]