from django.urls import path

from .views import (
    EcommerceStoreCreateView,
    EcommerceStoreListView,
    EcommerceStoreDetailView,
    EcommerceStoreDetailByUserView,
)

urlpatterns = [
    path("store/create/", EcommerceStoreCreateView.as_view()),
    path("store/list/", EcommerceStoreListView.as_view()),
    path("store/user/<int:user_id>/", EcommerceStoreDetailByUserView.as_view()),
    path("store/<int:pk>/", EcommerceStoreDetailView.as_view()),
]