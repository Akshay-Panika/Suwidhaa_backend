from django.urls import path

from .views import (
    NgoHistoryCreateView,
    NgoHistoryListView,
    NgoHistoryByDonorView,
    NgoHistoryByDonorDeleteView,
    NgoHistoryDetailView,
    NgoHistoryUpdateAmountView,
)

urlpatterns = [
    # ── Create ─────────────────────────────────────────────
    path(
        "history/create/",
        NgoHistoryCreateView.as_view(),
        name="ngo-history-create",
    ),

    # ── List (grouped) ─────────────────────────────────────
    path(
        "history/list/",
        NgoHistoryListView.as_view(),
        name="ngo-history-list",
    ),

    # ── Donor detail (GET) ─────────────────────────────────
    path(
        "history/donor/<int:donor_id>/",
        NgoHistoryByDonorView.as_view(),
        name="ngo-history-by-donor",
    ),

    # ── Donor delete (all donations) ───────────────────────
    path(
        "history/donor/<int:donor_id>/delete/",
        NgoHistoryByDonorDeleteView.as_view(),
        name="ngo-history-by-donor-delete",
    ),

    # ── Update amount (naya amount fill karo) ──────────────
    path(
        "history/<int:pk>/update-amount/",
        NgoHistoryUpdateAmountView.as_view(),
        name="ngo-history-update-amount",
    ),

    # ── Detail / Update / Delete ───────────────────────────
    path(
        "history/<int:pk>/",
        NgoHistoryDetailView.as_view(),
        name="ngo-history-detail",
    ),
]