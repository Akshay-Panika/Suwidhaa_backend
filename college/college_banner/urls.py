from django.urls import path

from .views import (
    CollegeBannerCreateView,
    CollegeBannerListView,
    CollegeBannerDetailView,
)


urlpatterns = [
    path(
        "college-banner/create/",
        CollegeBannerCreateView.as_view()
    ),
    path(
        "college-banner/list/",
        CollegeBannerListView.as_view()
    ),
    path(
        "college-banner/<int:pk>/",
        CollegeBannerDetailView.as_view()
    ),
]
