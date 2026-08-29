from django.urls import path
from .views import (
    TeacherCreateView,
    TeacherListView,
    TeacherDetailView,
    TeacherResendWhatsAppCredentialsView  
)

urlpatterns = [
    path("teacher/create/", TeacherCreateView.as_view(), name="teacher-create"),
    path("teacher/list/", TeacherListView.as_view(), name="teacher-list"),
    path("teacher/<int:pk>/", TeacherDetailView.as_view(), name="teacher-detail"),
    path("teacher/resend-whatsapp/", TeacherResendWhatsAppCredentialsView.as_view()),

]