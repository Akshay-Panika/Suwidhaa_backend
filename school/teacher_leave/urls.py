from django.urls import path
from .views import (
    TeacherLeaveCreateView,
    TeacherLeaveListView,
    TeacherLeaveDetailView,
    TeacherLeaveByIdCardView,
    TeacherLeaveByTeacherIdView,   # ✅ NEW
    TeacherLeaveBySchoolView,      # ✅ NEW
)

urlpatterns = [
    # CREATE
    path(
        "teacher-leave/create/",
        TeacherLeaveCreateView.as_view(),
        name="teacher-leave-create",
    ),

    # LIST ALL
    path(
        "teacher-leave/list/",
        TeacherLeaveListView.as_view(),
        name="teacher-leave-list",
    ),

    # ✅ SPECIFIC: by DB int id (must come before generic)
    path(
        "teacher-leave/teacher/<str:teacher_id>/",
        TeacherLeaveByTeacherIdView.as_view(),
        name="teacher-leave-by-teacher-id",
    ),

    # ✅ SPECIFIC: school-wise
    path(
        "teacher-leave/school/<int:school_id>/",
        TeacherLeaveBySchoolView.as_view(),
        name="teacher-leave-by-school",
    ),

    # SPECIFIC: by id_card
    path(
        "teacher-leave/list/<str:teacher_id_card>/",
        TeacherLeaveByIdCardView.as_view(),
        name="teacher-leave-by-id-card",
    ),

    # GENERIC: detail/update/delete
    path(
        "teacher-leave/<int:pk>/",
        TeacherLeaveDetailView.as_view(),
        name="teacher-leave-detail",
    ),
]