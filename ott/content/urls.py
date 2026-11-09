from django.urls import path
from .views import ContentListCreateAPIView, ContentDetailAPIView

urlpatterns = [
    path("content/create/", ContentListCreateAPIView.as_view(), name="content-create"),
    path("content/list/",   ContentListCreateAPIView.as_view(), name="content-list"),
    path("content/<int:pk>/", ContentDetailAPIView.as_view(), name="content-detail"),
]