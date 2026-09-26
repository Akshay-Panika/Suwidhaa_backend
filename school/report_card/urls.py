from django.urls import path
from .views import (
    ReportCardCreateView,
    ReportCardListView,
    ReportCardDetailView,
    ReportCardByAdminIdView,
)

urlpatterns = [
    # Create
    path(
        'report-cards/create/',
        ReportCardCreateView.as_view(),
        name='report-card-create',
    ),

    # List
    path(
        'report-cards/list/',
        ReportCardListView.as_view(),
        name='report-card-list',
    ),

    # Detail by id (GET / PUT / PATCH / DELETE)
    path(
        'report-cards/list/<int:pk>/',
        ReportCardDetailView.as_view(),
        name='report-card-detail',
    ),

    # List by admin_id
    path(
        'report-cards/adminid/<str:admin_id>/',
        ReportCardByAdminIdView.as_view(),
        name='report-card-by-admin',
    ),
]