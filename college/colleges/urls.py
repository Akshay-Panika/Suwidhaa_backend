from django.urls import path
from .views import (
    CollegeCreateView,
    CollegeListView,
    CollegeListByUserView,   # ✅ NEW
    CollegeDetailView,
)

urlpatterns = [
    path("colleges/create/", CollegeCreateView.as_view(), name="college-create"),
    path("colleges/list/", CollegeListView.as_view(), name="college-list"),
    path("colleges/list/<str:user_id>/", CollegeListByUserView.as_view(), name="college-list-by-user"),  # ✅ NEW
    path("colleges/<int:pk>/", CollegeDetailView.as_view(), name="college-detail"),
]