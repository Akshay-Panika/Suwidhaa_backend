from django.urls import path
from .views import WebseriesListAPIView

urlpatterns = [
    path("webseries/list/", WebseriesListAPIView.as_view(), name="webseries-list"),
]