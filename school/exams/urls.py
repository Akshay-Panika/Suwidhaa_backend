# school/exams/urls.py
from django.urls import path
from .views import (
    ClassExamTimetableCreateView,
    ClassExamTimetableListView,
    ClassExamTimetableDetailView,
)

urlpatterns = [
    path(
        'exam-timetables/create/',
        ClassExamTimetableCreateView.as_view(),
        name='exam-timetable-create',
    ),
    path(
        'exam-timetables/list/',
        ClassExamTimetableListView.as_view(),
        name='exam-timetable-list',
    ),
    path(
        'exam-timetables/<int:pk>/',
        ClassExamTimetableDetailView.as_view(),
        name='exam-timetable-detail',
    ),
]