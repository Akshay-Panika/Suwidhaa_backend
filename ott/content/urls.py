from django.urls import path
from .views import ContentListAPIView, ContentDetailAPIView

urlpatterns = [
    path('content/list/', ContentListAPIView.as_view(), name='content-list'),
    path('content/<int:pk>/', ContentDetailAPIView.as_view(), name='content-detail'),
]