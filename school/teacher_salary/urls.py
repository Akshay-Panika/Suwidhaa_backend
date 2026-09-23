from django.urls import path

from .views import (
    TeacherSalarySummaryView,
)

urlpatterns = [
    # GET + POST
    path(
        "teacher/salary/summary/<str:teacher_id_card>/",
        TeacherSalarySummaryView.as_view(),
        name="salary-summary",
    ),
]