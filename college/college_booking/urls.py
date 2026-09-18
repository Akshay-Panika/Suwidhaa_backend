# college/college_booking/urls.py

from django.urls import path
from .views import (
    CollegeBookingCreateView,
    CollegeBookingListView,
    CollegeBookingDetailView,
)

urlpatterns = [
    path("college-booking/create/", CollegeBookingCreateView.as_view(), name="college-booking-create"),
    path("college-booking/list/", CollegeBookingListView.as_view(), name="college-booking-list"),
    path("college-booking/<int:pk>/", CollegeBookingDetailView.as_view(), name="college-booking-detail"),
]