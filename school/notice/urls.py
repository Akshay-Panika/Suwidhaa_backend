from django.urls import path
from .views import (
    NoticeCreateAPIView,
    NoticeListAPIView,
    NoticeDetailAPIView,
    NoticeTogglePinAPIView,
)

urlpatterns = [
    path("notice/create/", NoticeCreateAPIView.as_view(), name="notice-create"),
    path("notice/list/", NoticeListAPIView.as_view(), name="notice-list"),
    path("notice/<int:pk>/", NoticeDetailAPIView.as_view(), name="notice-detail"),
    path(
        "notice/<int:pk>/toggle-pin/",
        NoticeTogglePinAPIView.as_view(),
        name="notice-toggle-pin",
    ),
]