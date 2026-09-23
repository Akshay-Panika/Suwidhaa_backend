from django.urls import path

from .views import (
    TeacherSalarySummaryView,
    TeacherSalaryDeleteMonthView,
)

urlpatterns = [
    # GET + POST
    path(
        "teacher/salary/summary/<str:teacher_id_card>/",
        TeacherSalarySummaryView.as_view(),
        name="salary-summary",
    ),

    # DELETE by month + year
    path(
        "teacher/salary/summary/<str:teacher_id_card>/<str:year>/<str:month>/",
        TeacherSalaryDeleteMonthView.as_view(),
        name="salary-delete-month",
    ),
]