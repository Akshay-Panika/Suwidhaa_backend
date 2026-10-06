from django.urls import path

from .views import (
    NgoServiceCreateView,
    NgoServiceListView,
    NgoServiceDetailView,
)


urlpatterns = [
    path(
        "service/create/",
        NgoServiceCreateView.as_view(),
    ),
    path(
        "service/list/",
        NgoServiceListView.as_view(),
    ),
    path(
        "service/<int:pk>/",
        NgoServiceDetailView.as_view(),
    ),
]