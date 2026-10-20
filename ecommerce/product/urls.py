from django.urls import path

from .views import (
    EcommerceProductCreateView,
    EcommerceProductAllView,
    EcommerceProductOwnerView,
    EcommerceProductFeedView,
    EcommerceProductDetailView,
    EcommerceFavoriteToggleView,
    EcommerceFavoriteListView,
    # CART
    EcommerceCartAddView,
    EcommerceCartListView,
    EcommerceCartRemoveView,
)

urlpatterns = [
    path("product/create/", EcommerceProductCreateView.as_view()),
    path("product/all/", EcommerceProductAllView.as_view()),
    path("product/owner/<int:user_id>/", EcommerceProductOwnerView.as_view()),
    path("product/feed/<int:user_id>/", EcommerceProductFeedView.as_view()),
    path("product/favorites/<int:user_id>/", EcommerceFavoriteListView.as_view()),
    path("product/<int:pk>/favorite/toggle/", EcommerceFavoriteToggleView.as_view()),

    # CART
    path("product/cart/<int:user_id>/", EcommerceCartListView.as_view()),
    path("product/<int:pk>/cart/add/", EcommerceCartAddView.as_view()),
    path("product/<int:pk>/cart/remove/", EcommerceCartRemoveView.as_view()),

    path("product/<int:pk>/", EcommerceProductDetailView.as_view()),
]