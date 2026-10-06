from django.urls import path

from .views import (
    NgoBannerCreateView,
    NgoBannerListView,
    NgoBannerDetailView,
)


urlpatterns = [
    path(
        "banner/create/",
        NgoBannerCreateView.as_view(),
    ),
    path(
        "banner/list/",
        NgoBannerListView.as_view(),
    ),
    path(
        "banner/<int:pk>/",
        NgoBannerDetailView.as_view(),
    ),
]