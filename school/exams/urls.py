from django.urls import path
from .views import (
    ClassExamTimetableCreateView,
    ClassExamTimetableListView,
    ClassExamTimetableDetailView,
)

urlpatterns = [
    path('<int:school_id>/exam-timetables/create/', ClassExamTimetableCreateView.as_view(), name='exam-timetable-create'),
    path('<int:school_id>/exam-timetables/list/', ClassExamTimetableListView.as_view(), name='exam-timetable-list'),
    path('<int:school_id>/exam-timetables/<int:pk>/', ClassExamTimetableDetailView.as_view(), name='exam-timetable-detail'),
]