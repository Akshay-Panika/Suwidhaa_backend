from django.urls import path
from .views import (
    ItServiceAdCreateView,
    ItServiceAdListView,
    ItServiceAdDetailView,
)

urlpatterns = [
    path("ad/create/", ItServiceAdCreateView.as_view()),
    path("ad/list/", ItServiceAdListView.as_view()),
    path("ad/<int:pk>/", ItServiceAdDetailView.as_view()),
]