from django.urls import path
from .views import (
    StudentLeaveCreateView,
    StudentLeaveListView,
    StudentLeaveDetailView,
    StudentLeaveByIdCardView,
    StudentLeaveBySchoolView,
    StudentLeaveByClassView,
    StudentLeaveApprovalView,
)

urlpatterns = [
    # Create / List (list supports ?school_id=&student_class=&student_id_card=&leave_status=)
    path("student-leave/create/", StudentLeaveCreateView.as_view()),
    path("student-leave/list/", StudentLeaveListView.as_view()),

    # ✅ School id wise
    path(
        "student-leave/list/school/<int:school_id>/",
        StudentLeaveBySchoolView.as_view(),
        name="student-leave-by-school",
    ),

    # ✅ Class wise
    path(
        "student-leave/list/class/<str:student_class>/",
        StudentLeaveByClassView.as_view(),
        name="student-leave-by-class",
    ),

    # ✅ Student id card wise (keep last – most generic)
    path(
        "student-leave/list/<str:student_id_card>/",
        StudentLeaveByIdCardView.as_view(),
        name="student-leave-by-id-card",
    ),

    # Detail / approval
    path("student-leave/<int:pk>/", StudentLeaveDetailView.as_view()),
    path("student-leave/approval/<int:pk>/", StudentLeaveApprovalView.as_view()),
]