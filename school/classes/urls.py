from django.urls import path
from .views import (
    ClassCreateView,
    ClassListView,
    ClassDetailView,
)

urlpatterns = [
    path("class/create/", ClassCreateView.as_view()),
    path("class/list/", ClassListView.as_view()),
    path("class/<int:pk>/", ClassDetailView.as_view()),
]