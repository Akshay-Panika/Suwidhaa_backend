from django.urls import path
from .views import ReportCardListCreateView, ReportCardDetailView

urlpatterns = [
    path('report-cards/', ReportCardListCreateView.as_view(), name='report-card-list-create'),
    path('report-cards/<int:pk>/', ReportCardDetailView.as_view(), name='report-card-detail'),
]