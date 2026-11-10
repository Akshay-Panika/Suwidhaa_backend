from django.urls import path
from .views import TvshowsListAPIView

urlpatterns = [
    path("tvshows/list/", TvshowsListAPIView.as_view(), name="tvshows-list"),
]