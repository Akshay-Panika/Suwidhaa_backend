from django.urls import path

from .views import (
    EcommerceProductCreateView,
    EcommerceProductListView,
    EcommerceProductListByUserView,
    EcommerceProductDetailView,
    EcommerceFavoriteToggleView,
    EcommerceFavoriteListView,
)

urlpatterns = [
    path("product/create/", EcommerceProductCreateView.as_view()),
    path("product/list/", EcommerceProductListView.as_view()),
    path("product/list/favorite/", EcommerceFavoriteListView.as_view()),
    path("product/list/user/<int:user_id>/", EcommerceProductListByUserView.as_view()),
    path("product/<int:pk>/favorite/toggle/", EcommerceFavoriteToggleView.as_view()),
    path("product/<int:pk>/", EcommerceProductDetailView.as_view()),
]