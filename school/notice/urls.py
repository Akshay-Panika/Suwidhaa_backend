from django.urls import path
from .views import (
    NoticeCreateAPIView,
    NoticeListAPIView, 
    NoticeListBySchoolAPIView,
    NoticeDetailAPIView,
    NoticeTogglePinAPIView,
)

urlpatterns = [
    path("notice/create/", NoticeCreateAPIView.as_view(), name="notice-create"),
    
    # ✅ List all notices (Bina school id ke)
    path("notice/list/", NoticeListAPIView.as_view(), name="notice-list"),
    
    # ✅ List notices by school
    path(
        "notice/list/school/<int:school_id>/",
        NoticeListBySchoolAPIView.as_view(),
        name="notice-list-by-school",
    ),
    path("notice/<int:pk>/", NoticeDetailAPIView.as_view(), name="notice-detail"),
    path("notice/<int:pk>/toggle-pin/", NoticeTogglePinAPIView.as_view(), name="notice-toggle-pin"),
]