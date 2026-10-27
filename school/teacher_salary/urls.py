from django.urls import path
from .views import TeacherSalaryListView

urlpatterns = [
    path("teacher/salary/list/", TeacherSalaryListView.as_view(), name="teacher-salary-list"),
]