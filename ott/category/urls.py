from django.urls import path
from .views import CategoryListCreateAPIView, CategoryDetailAPIView

urlpatterns = [
    path("category/create/", CategoryListCreateAPIView.as_view(), name="category-create"),
    path("category/list/", CategoryListCreateAPIView.as_view(), name="category-list"),
    path("category/<int:pk>/", CategoryDetailAPIView.as_view(), name="category-detail"),
]