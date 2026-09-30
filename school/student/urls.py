from django.urls import path
from .views import (
    StudentCreateView,
    StudentListView,
    StudentDetailView,
    ResendWhatsAppCredentialsView,
    StudentBySchoolTypeView,
)

urlpatterns = [
    path("student/create/", StudentCreateView.as_view()),
    path("student/list/", StudentListView.as_view()),
    path("student/list/school-type/<str:school_type>/", StudentBySchoolTypeView.as_view()),
    path("student/<int:pk>/", StudentDetailView.as_view()),
    path("student/resend-whatsapp/", ResendWhatsAppCredentialsView.as_view()),
]