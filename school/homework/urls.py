from django.urls import path
from .views import (
    HomeworkCreateView,
    HomeworkListView,
    HomeworkListSchoolWithClassView,
    HomeworkDetailView,
)

urlpatterns = [
    # POST /api/v1/school/homework/create/
    path(
        "homework/create/",
        HomeworkCreateView.as_view(),
        name="homework_create",
    ),

    # GET /api/v1/school/homework/list/
    path(
        "homework/list/",
        HomeworkListView.as_view(),
        name="homework_list",
    ),

    # GET /api/v1/school/homework/list/<school_type>/<class_name>/
    path(
        "homework/list/<str:school_type>/<str:class_name>/",
        HomeworkListSchoolWithClassView.as_view(),
        name="homework_list_by_type_class",
    ),

    # GET / PUT / PATCH / DELETE /api/v1/school/homework/<id>/
    path(
        "homework/<int:pk>/",
        HomeworkDetailView.as_view(),
        name="homework_detail",
    ),
]