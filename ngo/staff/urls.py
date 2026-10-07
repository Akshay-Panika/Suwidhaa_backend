from django.urls import path
from .views import (
    NgoStaffCreateView,
    NgoStaffListView,
    NgoStaffDetailView,
)

urlpatterns = [
    path("staff/list/", NgoStaffListView.as_view(), name="ngo-staff-list"),
    path("staff/create/", NgoStaffCreateView.as_view(), name="ngo-staff-create"),
    path("staff/<int:pk>/", NgoStaffDetailView.as_view(), name="ngo-staff-detail"),
]