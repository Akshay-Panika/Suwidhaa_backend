from django.urls import path
from .views import (
    StudentFeeListView, StudentFeeBySchoolView, 
    StudentFeeTransactionCreateView, StudentFeeTransactionHistoryView, 
    StudentFeeTransactionDeleteView
)

urlpatterns = [
    path("student/fee/list/", StudentFeeListView.as_view()),
    path("student/fee/list/school/<int:school_id>/", StudentFeeBySchoolView.as_view()),
    path("student/fee/transaction/create/", StudentFeeTransactionCreateView.as_view()),
    path("student/fee/transaction/history/<int:student_id>/", StudentFeeTransactionHistoryView.as_view()),
    path("student/fee/transaction/<int:student_id>/<int:transaction_id>/", StudentFeeTransactionDeleteView.as_view()),
]