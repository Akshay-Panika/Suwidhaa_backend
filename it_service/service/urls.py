from django.urls import path
from .views import (
    ItServiceServiceCreateView,
    ItServiceServiceListView,
    ItServiceServiceDetailView,
    BookedServiceListView,
    ItServiceServiceSearchView,
)

urlpatterns = [
    path("service/create/", ItServiceServiceCreateView.as_view()),
    path("service/list/", ItServiceServiceListView.as_view()),
    path("service/booked/list/", BookedServiceListView.as_view()),
    path("service/<int:pk>/", ItServiceServiceDetailView.as_view()),
    path("service/search/", ItServiceServiceSearchView.as_view()), 
]