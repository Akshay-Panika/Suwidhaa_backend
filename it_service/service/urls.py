from django.urls import path

from .views import (
    ItServiceServiceCreateView,
    ItServiceServiceListView,
    ItServiceServiceDetailView,
)

urlpatterns = [
    path("service/create/", ItServiceServiceCreateView.as_view()),
    path("service/list/", ItServiceServiceListView.as_view()),
    path("service/<int:pk>/", ItServiceServiceDetailView.as_view()),
]