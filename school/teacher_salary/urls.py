from django.urls import path
from .views import TeacherSalaryListView, TeacherSalaryTransactionCreateView

urlpatterns = [
    path("teacher/salary/list/", TeacherSalaryListView.as_view(), name="teacher-salary-list"),
    path("teacher/salary/transaction/create/", TeacherSalaryTransactionCreateView.as_view(), name="teacher-salary-transaction-create"),
]