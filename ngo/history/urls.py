from django.urls import path
from .views import (
    NgoHistoryCreateView,
    NgoHistoryListView,
    NgoHistoryByDonorView,
    NgoHistoryDetailView,
)

urlpatterns = [
    path("history/create/", NgoHistoryCreateView.as_view(), name="ngo-history-create"),
    path("history/list/", NgoHistoryListView.as_view(), name="ngo-history-list"), # 👈 Ab ye grouped data dega
    path("history/donor/<int:donor_id>/", NgoHistoryByDonorView.as_view(), name="ngo-history-by-donor"),
    path("history/<int:pk>/", NgoHistoryDetailView.as_view(), name="ngo-history-detail"),
]