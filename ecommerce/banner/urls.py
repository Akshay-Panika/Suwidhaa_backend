from django.urls import path

from .views import (
    EcommerceBannerCreateView,
    EcommerceBannerListView,
    EcommerceBannerDetailView,
)

urlpatterns = [
    path("banner/create/", EcommerceBannerCreateView.as_view()),
    path("banner/list/", EcommerceBannerListView.as_view()),
    path("banner/<int:pk>/", EcommerceBannerDetailView.as_view()),
]