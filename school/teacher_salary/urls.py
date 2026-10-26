# school/teacher_salary/urls.py
from django.urls import path
from .views import (
    TeacherSalaryListView,
    TeacherSalaryListBySchoolView,
    TeacherSalarySummaryView,
    TeacherSalaryDeleteMonthView,
)

urlpatterns = [
    path("teacher/salary/list/", TeacherSalaryListView.as_view(), name="salary-list"),
    path("teacher/salary/list/school/<int:school_id>/", TeacherSalaryListBySchoolView.as_view(), name="salary-list-by-school"),
    path("teacher/salary/summary/<str:teacher_id_card>/", TeacherSalarySummaryView.as_view(), name="salary-summary"),
    path("teacher/salary/summary/<str:teacher_id_card>/<str:year>/<str:month>/", TeacherSalaryDeleteMonthView.as_view(), name="salary-delete-month"),
]