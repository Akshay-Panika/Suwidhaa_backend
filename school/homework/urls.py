from django.urls import path
from .views import (
    HomeworkCreateView,
    HomeworkListView,
    HomeworkByTeacherView,
    HomeworkDetailView,
    HomeworkStudentToggleView,  
)

urlpatterns = [
    path("homework/create/", HomeworkCreateView.as_view(), name="homework-create"),
    path("homework/list/", HomeworkListView.as_view(), name="homework-list"),
    path("homework/list/<str:teacher_id>/", HomeworkByTeacherView.as_view(), name="homework-list-by-teacher"),

    # ⬇️ NEW — toggle status of a specific student inside a homework
    path(
        "homework/<int:homework_id>/students/<int:student_pk>/toggle/",
        HomeworkStudentToggleView.as_view(),
        name="homework-student-toggle"
    ),

    path("homework/<int:pk>/", HomeworkDetailView.as_view(), name="homework-detail"),
]