from django.urls import path

from .views import (
    EcommerceCategoryCreateView,
    EcommerceCategoryListView,
    EcommerceCategoryDetailView,
)

urlpatterns = [
    path("category/create/", EcommerceCategoryCreateView.as_view()),
    path("category/list/", EcommerceCategoryListView.as_view()),
    path("category/<int:pk>/", EcommerceCategoryDetailView.as_view()),
]