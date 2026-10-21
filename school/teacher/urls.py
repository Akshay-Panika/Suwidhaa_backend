from django.urls import path
from .views import (
    TeacherCreateView,
    TeacherListView,
    TeacherDetailView,
    ResendWhatsAppCredentialsView,
    TeacherBySchoolView,
)

urlpatterns = [
    path("teacher/create/", TeacherCreateView.as_view()),
    path("teacher/list/", TeacherListView.as_view()),
    path("teacher/list/school/<int:school_id>/", TeacherBySchoolView.as_view()),
    path("teacher/<int:pk>/", TeacherDetailView.as_view()),
    path("teacher/resend-whatsapp/", ResendWhatsAppCredentialsView.as_view()),
]