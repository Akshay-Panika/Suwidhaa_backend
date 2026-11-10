from django.urls import path
from .views import (
    ClassListCreateAPIView, ClassDetailAPIView,
    SubjectListCreateAPIView, SubjectDetailAPIView,
    RecordVideoListCreateAPIView, RecordVideoDetailAPIView
)

urlpatterns = [
    # Class
    path('record-videos/classes/', ClassListCreateAPIView.as_view()),
    path('record-videos/classes/<int:pk>/', ClassDetailAPIView.as_view()),
    
    # ✅ Subject Class ke andar aayega
    path('record-videos/classes/<int:class_id>/subjects/', SubjectListCreateAPIView.as_view()),
    path('record-videos/classes/<int:class_id>/subjects/<int:pk>/', SubjectDetailAPIView.as_view()),
    
    # Video
    path('record-videos/classes/<int:class_id>/videos/', RecordVideoListCreateAPIView.as_view()),
    path('record-videos/classes/<int:class_id>/videos/<int:pk>/', RecordVideoDetailAPIView.as_view()),
]