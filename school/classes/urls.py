# school/classes/urls.py
from django.urls import path

from .views import (
    ClassCreateView,
    ClassBySchoolView,
    AssignClassTeacherView,
)

urlpatterns = [
    # 1. Create class (school_id wise)
    path("class/create/", ClassCreateView.as_view()),
    path("class/list/school/<int:school_id>/", ClassBySchoolView.as_view()),
    path("class/<int:pk>/assign-teacher/", AssignClassTeacherView.as_view()),
]