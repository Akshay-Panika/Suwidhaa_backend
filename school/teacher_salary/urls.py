from django.urls import path

from .views import (
    TeacherSalaryListCreateView,
    TeacherSalaryDetailView,
    TeacherSalarySummaryView,
    TeacherExtraSalaryListCreateView,
    TeacherExtraSalaryDetailView,
    TeacherSalaryRequestListCreateView,
    TeacherSalaryRequestDetailView,
    TeacherPendingSalaryListView,
    TeacherBankDetailView,
)

urlpatterns = [
    # Monthly salary
    path("salary/", TeacherSalaryListCreateView.as_view(), name="salary-list-create"),
    path("salary/<int:pk>/", TeacherSalaryDetailView.as_view(), name="salary-detail"),
    path("salary/summary/<str:teacher_id_card>/", TeacherSalarySummaryView.as_view(), name="salary-summary"),

    # Extra salary
    path("extra-salary/", TeacherExtraSalaryListCreateView.as_view(), name="extra-salary-list-create"),
    path("extra-salary/<int:pk>/", TeacherExtraSalaryDetailView.as_view(), name="extra-salary-detail"),

    # Salary requests
    path("requests/", TeacherSalaryRequestListCreateView.as_view(), name="salary-request-list-create"),
    path("requests/<int:pk>/", TeacherSalaryRequestDetailView.as_view(), name="salary-request-detail"),

    # Pending salary
    path("pending/", TeacherPendingSalaryListView.as_view(), name="pending-salary-list"),

    # Bank details
    path("bank/<str:teacher_id_card>/", TeacherBankDetailView.as_view(), name="bank-detail"),
]