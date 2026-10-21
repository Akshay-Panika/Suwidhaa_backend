from django.urls import path
from .views import (
    SchoolTypeCreateView,
    SchoolTypeListView,
    SchoolTypeDetailView,
)

urlpatterns = [
    path("school-type/create/", SchoolTypeCreateView.as_view()),
    path("school-type/list/", SchoolTypeListView.as_view()),
    path("school-type/<int:pk>/", SchoolTypeDetailView.as_view()),
]