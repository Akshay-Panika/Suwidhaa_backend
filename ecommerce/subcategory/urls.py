from django.urls import path

from .views import (
    EcommerceSubcategoryCreateView,
    EcommerceSubcategoryListView,
    EcommerceSubcategoryDetailView,
)

urlpatterns = [
    path("subcategory/create/", EcommerceSubcategoryCreateView.as_view()),
    path("subcategory/list/", EcommerceSubcategoryListView.as_view()),
    path("subcategory/<int:pk>/", EcommerceSubcategoryDetailView.as_view()),
]