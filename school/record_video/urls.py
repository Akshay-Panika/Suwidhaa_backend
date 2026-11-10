from django.urls import path
from .views import ClassListView, SubjectListView, RecordVideoListView

urlpatterns = [
    path('classes/', ClassListView.as_view(), name='record-video-classes'),
    path('subjects/', SubjectListView.as_view(), name='record-video-subjects'),
    path('classes/<int:class_id>/videos/', RecordVideoListView.as_view(), name='record-video-list'),
]