from django.urls import path
from .views import (
    NoticeCreateAPIView,
    NoticeListBySchoolAPIView,
    NoticeDetailAPIView,
    NoticeTogglePinAPIView,
)

urlpatterns = [
    path("notice/create/", NoticeCreateAPIView.as_view(), name="notice-create"),
    path(
        "notice/list/school/<int:school_id>/",
        NoticeListBySchoolAPIView.as_view(),
        name="notice-list-by-school",
    ),
    path(
        "notice/<int:pk>/",
        NoticeDetailAPIView.as_view(),
        name="notice-detail",
    ),
    path(
        "notice/<int:pk>/toggle-pin/",
        NoticeTogglePinAPIView.as_view(),
        name="notice-toggle-pin",
    ),
]