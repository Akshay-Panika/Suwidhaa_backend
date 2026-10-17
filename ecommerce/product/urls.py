from django.urls import path

from .views import (
    EcommerceProductCreateView,
    EcommerceProductListView,
    EcommerceProductDetailView,
)

urlpatterns = [
    path("product/create/", EcommerceProductCreateView.as_view()),
    path("product/list/", EcommerceProductListView.as_view()),
    path("product/<int:pk>/", EcommerceProductDetailView.as_view()),
]