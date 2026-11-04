from django.urls import path
from .views import (
    HomeworkCreateView,
    HomeworkListView,
    HomeworkListByTeacherView,
    HomeworkListByStudentView,        # ✅ NEW
    HomeworkDetailView,
    HomeworkToggleStudentStatusView,
)

urlpatterns = [
    # POST /api/v1/school/homework/create/
    path(
        "homework/create/",
        HomeworkCreateView.as_view(),
        name="homework_create",
    ),

    # GET /api/v1/school/homework/list/
    path(
        "homework/list/",
        HomeworkListView.as_view(),
        name="homework_list",
    ),

    # POST /api/v1/school/homework/<pk>/toggle-status/<student_idcard>/
    path(
        "homework/<int:pk>/toggle-status/<str:student_idcard>/",
        HomeworkToggleStudentStatusView.as_view(),
        name="homework_toggle_student_status",
    ),

    # ✅ SPECIFIC: teacher-id (must come before generic patterns)
    # GET /api/v1/school/homework/list/teacher-id/<teacher_id>/
    path(
        "homework/list/teacher-id/<str:teacher_id>/",
        HomeworkListByTeacherView.as_view(),
        name="homework_list_by_teacher",
    ),

    # ✅ SPECIFIC: student-id (must come before generic patterns)
    # GET /api/v1/school/homework/list/student-id/<student_idcard>/
    path(
        "homework/list/student-id/<str:student_idcard>/",
        HomeworkListByStudentView.as_view(),
        name="homework_list_by_student",
    ),

    # GET / PUT / PATCH / DELETE /api/v1/school/homework/<id>/
    path(
        "homework/<int:pk>/",
        HomeworkDetailView.as_view(),
        name="homework_detail",
    ),
]