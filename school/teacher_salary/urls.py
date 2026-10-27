from django.urls import path
from .views import (
    TeacherSalaryListView, 
    TeacherSalaryTransactionCreateView,
    TeacherSalaryTransactionDetailView,
    TeacherTransactionHistoryView
)

urlpatterns = [
    path("teacher/salary/list/", TeacherSalaryListView.as_view(), name="teacher-salary-list"),
    path("teacher/salary/transaction/create/", TeacherSalaryTransactionCreateView.as_view(), name="teacher-salary-transaction-create"),
    path("teacher/salary/transaction/<int:teacher_id>/<int:transaction_id>/", TeacherSalaryTransactionDetailView.as_view(), name="teacher-salary-transaction-detail"),
    path("teacher/salary/transaction/history/<int:teacher_id>/", TeacherTransactionHistoryView.as_view(), name="teacher-transaction-history"),
]