# school/teacher_salary/urls.py
from django.urls import path
from .views import (
    TeacherSalaryListView,
    TeacherSalaryListBySchoolView,
)

urlpatterns = [
    path(
        "teacher/salary/list/",
        TeacherSalaryListView.as_view(),
        name="salary-list",
    ),
    path(
        "teacher/salary/list/school/<int:school_id>/",
        TeacherSalaryListBySchoolView.as_view(),
        name="salary-list-by-school",
    ),
]