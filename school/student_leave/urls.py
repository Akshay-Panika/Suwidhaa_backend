from django.urls import path
from .views import (
    StudentLeaveCreateView,
    StudentLeaveListView,
    StudentLeaveDetailView,
    StudentLeaveByIdCardView,
    StudentLeaveApprovalView,
)

urlpatterns = [
    path("student-leave/create/", StudentLeaveCreateView.as_view(), name="student-leave-create"),
    path("student-leave/list/", StudentLeaveListView.as_view(), name="student-leave-list"),
    path("student-leave/<int:pk>/", StudentLeaveDetailView.as_view(), name="student-leave-detail"),
    path(
        "student-leave/list/<str:student_id_card>/",
        StudentLeaveByIdCardView.as_view(),
        name="student-leave-by-id-card",
    ),
    # NEW: Teacher approval / rejection
    path(
        "student-leave/approval/<int:pk>/",
        StudentLeaveApprovalView.as_view(),
        name="student-leave-approval",
    ),
]