from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def home(request):
    return JsonResponse({
        "success": True,
        "message": "Suwidhaa Backend API is running",
    })


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),

    # ---------- school ----------
    path("api/v1/school/", include("school.school_type.urls")),
    path("api/v1/school/", include("school.student.urls")),
    path("api/v1/school/", include("school.teacher.urls")),
    path("api/v1/school/", include("school.teacher_attendance.urls")),
    path("api/v1/school/", include("school.student_attendance.urls")),
    path("api/v1/school/", include("school.teacher_leave.urls")),
    path("api/v1/school/", include("school.teacher_salary.urls")),
    path("api/v1/school/", include("school.student_leave.urls")),
    path("api/v1/school/", include("school.student_fee.urls")),
    path("api/v1/school/", include("school.classes.urls")),
    path("api/v1/school/", include("school.subject.urls")),
    path("api/v1/school/", include("school.student_pass.urls")),
    path("api/v1/school/", include("school.teacher_pass.urls")),
    path("api/v1/school/", include("school.homework.urls")),
    path("api/v1/school/", include("school.transport.urls")),
    path("api/v1/school/", include("school.report_card.urls")),
    path("api/v1/school/", include("school.meeting.urls")),
    path("api/v1/school/", include("school.notice.urls")),
    path("api/v1/school/", include("school.event.urls")),
    path("api/v1/school/", include("school.library.urls")),
    path("api/v1/school/", include("school.exams.urls")),

    # ---------- college ----------
    path("api/v1/college/", include("college.college_banner.urls")),
    path("api/v1/college/", include("college.colleges.urls")),
    path("api/v1/college/", include("college.college_booking.urls")),
    path("api/v1/college/", include("college.room.urls")),
    path("api/v1/college/", include("college.tiffin.urls")),

    # ---------- auth ----------
    path("api/v1/auth/", include("auth.app_auth.urls")),
    path("api/v1/profile/", include("auth.app_profile.urls")),

    # ---------- ott ----------
    path("api/v1/ott/", include("ott.category.urls")),
    path("api/v1/ott/", include("ott.content.urls")),
    path("api/v1/ott/", include("ott.webseries.urls")),
    path("api/v1/ott/", include("ott.banner.urls")),
    path("api/v1/ott/", include("ott.reels.urls")),
    path("api/v1/ott/", include("ott.ads.urls")),

    # ---------- ngo ----------
    path("api/v1/ngo/", include("ngo.banner.urls")),
    path("api/v1/ngo/", include("ngo.category.urls")),
    path("api/v1/ngo/", include("ngo.service.urls")),
    path("api/v1/ngo/", include("ngo.staff.urls")),
    path("api/v1/ngo/", include("ngo.history.urls")),

    # ---------- it_service ----------
    path("api/v1/it_service/", include("it_service.banner.urls")),
    path("api/v1/it_service/", include("it_service.category.urls")),
    path("api/v1/it_service/", include("it_service.service.urls")),
    path("api/v1/it_service/", include("it_service.booking.urls")),

    # ---------- ecommerce ----------
    path("api/v1/ecommerce/", include("ecommerce.banner.urls")),
    path("api/v1/ecommerce/", include("ecommerce.category.urls")),
    path("api/v1/ecommerce/", include("ecommerce.subcategory.urls")),
    path("api/v1/ecommerce/", include("ecommerce.product.urls")),
    path("api/v1/ecommerce/", include("ecommerce.store.urls")),
]