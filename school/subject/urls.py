from django.urls import path
from .views import SubjectCreateView, SubjectBySchoolView, SubjectDetailView

urlpatterns = [
    path("subject/create/", SubjectCreateView.as_view()),
    path("subject/list/school/<int:school_id>/", SubjectBySchoolView.as_view()),
    path("subject/<int:pk>/", SubjectDetailView.as_view()),
]