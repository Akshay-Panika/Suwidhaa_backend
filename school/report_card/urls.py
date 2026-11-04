from django.urls import path
from .views import (
    ReportCardCreateView,
    ReportCardBulkCreateView,     # ✅ NEW
    ReportCardListView,
    ReportCardDetailView,
    ReportCardByStudentIdView,
    ReportCardByTeacherView,
)

urlpatterns = [
    # SINGLE CREATE
    path(
        'report-cards/create/',
        ReportCardCreateView.as_view(),
        name='report-card-create',
    ),

    # ✅ BULK CREATE (multi-student assign)
    path(
        'report-cards/bulk-create/',
        ReportCardBulkCreateView.as_view(),
        name='report-card-bulk-create',
    ),

    # LIST ALL
    path(
        'report-cards/list/',
        ReportCardListView.as_view(),
        name='report-card-list',
    ),

    # TEACHER-WISE
    path(
        'report-cards/teacher/<str:teacher_id>/',
        ReportCardByTeacherView.as_view(),
        name='report-card-by-teacher',
    ),

    # STUDENT-WISE (DB int id)
    path(
        'report-cards/student-list/<str:student_id>/',
        ReportCardByStudentIdView.as_view(),
        name='report-card-by-student',
    ),

    # DETAIL
    path(
        'report-cards/list/<int:pk>/',
        ReportCardDetailView.as_view(),
        name='report-card-detail',
    ),
]