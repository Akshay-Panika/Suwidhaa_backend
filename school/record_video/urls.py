from django.urls import path
from .views import (
    ClassListCreateAPIView, ClassDetailAPIView,
    SubjectListCreateAPIView, SubjectDetailAPIView,
    RecordVideoListCreateAPIView, RecordVideoDetailAPIView
)

urlpatterns = [
    # Class CRUD
    path('record-videos/classes/', ClassListCreateAPIView.as_view(), name='class-list'),
    path('record-videos/classes/<int:pk>/', ClassDetailAPIView.as_view(), name='class-detail'),
    
    # Subject CRUD
    path('record-videos/subjects/', SubjectListCreateAPIView.as_view(), name='subject-list'),
    path('record-videos/subjects/<int:pk>/', SubjectDetailAPIView.as_view(), name='subject-detail'),
    
    # Video CRUD
    path('record-videos/classes/<int:class_id>/videos/', RecordVideoListCreateAPIView.as_view(), name='video-list'),
    path('record-videos/classes/<int:class_id>/videos/<int:pk>/', RecordVideoDetailAPIView.as_view(), name='video-detail'),
]