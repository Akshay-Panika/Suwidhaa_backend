from django.urls import path

from .views import (
    EcommerceProductCreateView,
    EcommerceProductAllView,
    EcommerceProductOwnerView,
    EcommerceProductFeedView,
    EcommerceProductDetailView,
    EcommerceFavoriteToggleView,
    EcommerceFavoriteListView,
    EcommerceProductFeedBySubcategoryView,
)

urlpatterns = [
    path("product/create/", EcommerceProductCreateView.as_view()),
    path("product/all/", EcommerceProductAllView.as_view()),
    path("product/owner/<int:user_id>/", EcommerceProductOwnerView.as_view()),
    path("product/feed/<int:user_id>/", EcommerceProductFeedView.as_view()),
    path("product/feed/<int:user_id>/subcategory/<int:subcategory_id>/", EcommerceProductFeedBySubcategoryView.as_view()),
    path("product/favorites/<int:user_id>/", EcommerceFavoriteListView.as_view()),
    path("product/<int:pk>/favorite/toggle/", EcommerceFavoriteToggleView.as_view()),
    path("product/<int:pk>/", EcommerceProductDetailView.as_view()),
]