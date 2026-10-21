from django.urls import path
from .views import (
    StudentCreateView,
    StudentListView,
    StudentDetailView,
    ResendWhatsAppCredentialsView,
    StudentBySchoolView,
)

urlpatterns = [
    path("student/create/", StudentCreateView.as_view()),
    path("student/list/", StudentListView.as_view()),
    path("student/list/school/<int:school_id>/", StudentBySchoolView.as_view()),
    path("student/<int:pk>/", StudentDetailView.as_view()),
    path("student/resend-whatsapp/", ResendWhatsAppCredentialsView.as_view()),
]