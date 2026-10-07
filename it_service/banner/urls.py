from django.urls import path

from .views import (
    ItServiceBannerCreateView,
    ItServiceBannerListView,
    ItServiceBannerDetailView,
)

urlpatterns = [
    path("banner/create/", ItServiceBannerCreateView.as_view()),
    path("banner/list/", ItServiceBannerListView.as_view()),
    path("banner/<int:pk>/", ItServiceBannerDetailView.as_view()),
]