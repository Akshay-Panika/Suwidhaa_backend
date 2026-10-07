from django.urls import path

from .views import (
    ItServiceCategoryCreateView,
    ItServiceCategoryListView,
    ItServiceCategoryDetailView,
)

urlpatterns = [
    path("category/create/", ItServiceCategoryCreateView.as_view()),
    path("category/list/", ItServiceCategoryListView.as_view()),
    path("category/<int:pk>/", ItServiceCategoryDetailView.as_view()),
]