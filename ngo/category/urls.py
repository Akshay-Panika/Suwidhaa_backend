from django.urls import path

from .views import (
    NgoCategoryCreateView,
    NgoCategoryListView,
    NgoCategoryDetailView,
)


urlpatterns = [
    path(
        "category/create/",
        NgoCategoryCreateView.as_view(),
    ),
    path(
        "category/list/",
        NgoCategoryListView.as_view(),
    ),
    path(
        "category/<int:pk>/",
        NgoCategoryDetailView.as_view(),
    ),
]