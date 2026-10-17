from django.urls import path

from .views import (
    EcommerceProductCreateView,
    EcommerceProductListView,
    EcommerceProductDetailView,
    EcommerceProductByUserListView,   # <-- add
)

urlpatterns = [
    path("product/create/", EcommerceProductCreateView.as_view()),
    path("product/list/", EcommerceProductListView.as_view()),
    path("product/user/<int:user_id>/", EcommerceProductByUserListView.as_view()),
    path("product/<int:pk>/", EcommerceProductDetailView.as_view()),
]