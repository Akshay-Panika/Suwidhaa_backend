from django.urls import path
from .views import (
    TeacherLeaveCreateView,
    TeacherLeaveListView,
    TeacherLeaveDetailView,
    TeacherLeaveByIdCardView,
)

urlpatterns = [
    path("teacher-leave/create/", TeacherLeaveCreateView.as_view(), name="teacher-leave-create"),
    path("teacher-leave/list/", TeacherLeaveListView.as_view(), name="teacher-leave-list"),
    path("teacher-leave/<int:pk>/", TeacherLeaveDetailView.as_view(), name="teacher-leave-detail"),
    path("teacher-leave/list/<str:teacher_id_card>/", TeacherLeaveByIdCardView.as_view(), name="teacher-leave-by-id-card"),
]