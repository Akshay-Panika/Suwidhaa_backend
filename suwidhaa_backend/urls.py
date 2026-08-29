from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def home(request):
    return JsonResponse({
        "success": True,
        "message": "Suwidhaa Backend API is running",
    })


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path(
        "api/v1/school/",
        include("school.student.urls"),
    ),
    path(
         "api/v1/school/",
         include("school.teacher.urls"),
    ),
    path(
         "api/v1/school/",
         include("school.classes.urls"),
    ),
    path(
         "api/v1/school/",
         include("school.subject.urls"),
    ),
    path(
         "api/v1/school/",
         include("school.schedule.urls"),
    ),
    path(
        "api/v1/school/",
        include("school.student_pass.urls"),
    ),
    path(
        "api/v1/school/",
        include("school.teacher_pass.urls"),
    ),
]