# college/college_booking/urls.py

from django.urls import path
from .views import (
    CollegeBookingCreateView,
)

urlpatterns = [
    path("college-booking/create/", CollegeBookingCreateView.as_view(), name="college-booking-create"),
]