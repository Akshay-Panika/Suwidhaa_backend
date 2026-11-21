from django.urls import path

from .views import (
    CollegeCategoryCreateView,
    CollegeCategoryListView,
    CollegeCategoryDetailView,
)

urlpatterns = [
    path(
        "college-category/create/",
        CollegeCategoryCreateView.as_view(),
    ),
    path(
        "college-category/list/",
        CollegeCategoryListView.as_view(),
    ),
    path(
        "college-category/<int:pk>/",
        CollegeCategoryDetailView.as_view(),
    ),
]