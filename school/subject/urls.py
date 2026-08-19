from django.urls import path
from .views import (
    SubjectCreateView,
    SubjectListView,
    SubjectDetailView,
)

urlpatterns = [
    path("subject/create/", SubjectCreateView.as_view()),
    path("subject/list/", SubjectListView.as_view()),
    path("subject/<int:pk>/", SubjectDetailView.as_view()),
]