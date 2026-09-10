from django.urls import path
from .views import CartoonListCreateAPIView, CartoonDetailAPIView

urlpatterns = [
    path('cartoons/create/', CartoonListCreateAPIView.as_view(), name='cartoon-create'),
    path('cartoons/list/', CartoonListCreateAPIView.as_view(), name='cartoon-list'),
    path('cartoons/<int:pk>/', CartoonDetailAPIView.as_view(), name='cartoon-detail'),
]