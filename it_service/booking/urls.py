from django.urls import path

from .views import (
    BookingCreateView,
    BookingListView,
    BookingDetailView,
)

urlpatterns = [
    path("booking/create/", BookingCreateView.as_view()),
    path("booking/list/", BookingListView.as_view()),
    path("booking/<int:pk>/", BookingDetailView.as_view()),
]