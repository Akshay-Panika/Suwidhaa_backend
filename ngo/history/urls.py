from django.urls import path

from .views import (
    NgoHistoryCreateView,
    NgoHistoryListView,
    NgoHistoryByDonorView,
    NgoHistoryByDonorDeleteView,
    NgoHistoryDetailView,
    NgoHistoryResetAmountView,
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

    # ── Donor delete (all donations of a donor) ────────────
    path(
        "history/donor/<int:donor_id>/delete/",
        NgoHistoryByDonorDeleteView.as_view(),
        name="ngo-history-by-donor-delete",
    ),

    # ── Amount-only reset (record kept, amount → 0) ────────
    path(
        "history/<int:pk>/reset-amount/",
        NgoHistoryResetAmountView.as_view(),
        name="ngo-history-reset-amount",
    ),

    # ── Detail / Update / Delete ───────────────────────────
    path(
        "history/<int:pk>/",
        NgoHistoryDetailView.as_view(),
        name="ngo-history-detail",
    ),
]