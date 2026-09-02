from django.urls import path
from .views import (
    CollegeCreateView,
    CollegeListView,
    CollegeDetailView,
)

urlpatterns = [
    path(
        "colleges/create/",
        CollegeCreateView.as_view(),
        name="college-create"
    ),
    path(
        "colleges/list/",
        CollegeListView.as_view(),
        name="college-list"
    ),
    path(
        "colleges/<int:pk>/",
        CollegeDetailView.as_view(),
        name="college-detail"
    ),
]