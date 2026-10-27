from django.urls import path
from .views import (
    UserProfileListView,
    UserProfileDetailView,
    UserProfileCreateUpdateView,
    UserProfileDeleteView,
)

urlpatterns = [
    # 1. Get all profiles list
    path("list/", UserProfileListView.as_view(), name="profile-list"),
    
    # 2. Get profile by profile ID
    path("<int:profile_id>/", UserProfileDetailView.as_view(), name="profile-detail"),
    
    # 3. Add / Update profile by User ID
    path("user/<int:user_id>/", UserProfileCreateUpdateView.as_view(), name="profile-create-update"),
    
    # 4. Delete profile by profile ID
    path("delete/<int:profile_id>/", UserProfileDeleteView.as_view(), name="profile-delete"),
]