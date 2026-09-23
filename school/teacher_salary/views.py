import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from school.teacher.models import Teacher
from .models import (
    TeacherSalary,
    TeacherExtraSalary,
    TeacherSalaryRequest,
    TeacherPendingSalary,
    TeacherBankDetail,
)
from .serializers import (
    TeacherSalarySerializer,
    TeacherExtraSalarySerializer,
    TeacherSalaryRequestSerializer,
    TeacherPendingSalarySerializer,
    TeacherBankDetailSerializer,
)

logger = logging.getLogger(__name__)


# =====================================================================
# Helper: get teacher by teacher_id_card
# =====================================================================
def _get_teacher_by_card(teacher_id_card):
    try:
        return Teacher.objects.get(teacher_id_card=teacher_id_card)
    except Teacher.DoesNotExist:
        return None


# =====================================================================
# MONTHLY SALARY
# =====================================================================
class TeacherSalaryListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        """List salary records. Filter by ?teacher_id_card=...&year=...&month=..."""
        qs = TeacherSalary.objects.all().order_by("-id")

        teacher_id_card = request.query_params.get("teacher_id_card")
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        status_filter = request.query_params.get("status")

        if teacher_id_card:
            teacher = _get_teacher_by_card(teacher_id_card)
            if not teacher:
                return Response(
                    {"success": False, "message": "Teacher not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            qs = qs.filter(teacher=teacher)

        if year:
            qs = qs.filter(year=year)
        if month and month != "All":
            qs = qs.filter(month=month)
        if status_filter and status_filter != "All":
            qs = qs.filter(status=status_filter)

        serializer = TeacherSalarySerializer(qs, many=True)
        return Response(
            {"success": True, "count": qs.count(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Create a salary record."""
        teacher_id_card = request.data.get("teacher_id_card")
        if not teacher_id_card:
            return Response(
                {"success": False, "message": "teacher_id_card is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        teacher = _get_teacher_by_card(teacher_id_card)
        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data["teacher"] = teacher.id

        serializer = TeacherSalarySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Salary record created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TeacherSalaryDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return TeacherSalary.objects.get(pk=pk)
        except TeacherSalary.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "Salary not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"success": True, "data": TeacherSalarySerializer(obj).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "Salary not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TeacherSalarySerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Salary updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "Salary not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TeacherSalarySerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Salary updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "Salary not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        obj.delete()
        return Response(
            {"success": True, "message": "Salary deleted"},
            status=status.HTTP_200_OK,
        )


# =====================================================================
# SALARY SUMMARY (by teacher id card)
# =====================================================================
class TeacherSalarySummaryView(APIView):
    """Returns salary summary for a teacher: total, paid, pending, latest month."""

    def get(self, request, teacher_id_card):
        teacher = _get_teacher_by_card(teacher_id_card)
        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        qs = TeacherSalary.objects.filter(teacher=teacher)

        total = sum(float(s.amount or 0) for s in qs)
        paid = sum(float(s.paid_amount or 0) for s in qs)
        pending = sum(float(s.pending_amount or 0) for s in qs)

        latest = qs.order_by("-id").first()
        latest_data = (
            TeacherSalarySerializer(latest).data if latest else None
        )

        return Response(
            {
                "success": True,
                "data": {
                    "teacher_id_card": teacher.teacher_id_card,
                    "teacher_name": f"{teacher.first_name} {teacher.last_name}",
                    "total_salary": total,
                    "paid_amount": paid,
                    "pending_amount": pending,
                    "latest_salary": latest_data,
                },
            },
            status=status.HTTP_200_OK,
        )


# =====================================================================
# EXTRA SALARY
# =====================================================================
class TeacherExtraSalaryListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = TeacherExtraSalary.objects.all().order_by("-id")

        teacher_id_card = request.query_params.get("teacher_id_card")
        if teacher_id_card:
            teacher = _get_teacher_by_card(teacher_id_card)
            if not teacher:
                return Response(
                    {"success": False, "message": "Teacher not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            qs = qs.filter(teacher=teacher)

        serializer = TeacherExtraSalarySerializer(qs, many=True)
        return Response(
            {"success": True, "count": qs.count(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        teacher_id_card = request.data.get("teacher_id_card")
        if not teacher_id_card:
            return Response(
                {"success": False, "message": "teacher_id_card is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        teacher = _get_teacher_by_card(teacher_id_card)
        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data["teacher"] = teacher.id

        serializer = TeacherExtraSalarySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Extra salary added",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TeacherExtraSalaryDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return TeacherExtraSalary.objects.get(pk=pk)
        except TeacherExtraSalary.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "Extra salary not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"success": True, "data": TeacherExtraSalarySerializer(obj).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "Extra salary not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TeacherExtraSalarySerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "Extra salary not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        obj.delete()
        return Response(
            {"success": True, "message": "Extra salary deleted"},
            status=status.HTTP_200_OK,
        )


# =====================================================================
# SALARY REQUESTS
# =====================================================================
class TeacherSalaryRequestListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = TeacherSalaryRequest.objects.all().order_by("-id")

        teacher_id_card = request.query_params.get("teacher_id_card")
        if teacher_id_card:
            teacher = _get_teacher_by_card(teacher_id_card)
            if not teacher:
                return Response(
                    {"success": False, "message": "Teacher not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            qs = qs.filter(teacher=teacher)

        serializer = TeacherSalaryRequestSerializer(qs, many=True)
        return Response(
            {"success": True, "count": qs.count(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        teacher_id_card = request.data.get("teacher_id_card")
        if not teacher_id_card:
            return Response(
                {"success": False, "message": "teacher_id_card is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        teacher = _get_teacher_by_card(teacher_id_card)
        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data["teacher"] = teacher.id

        serializer = TeacherSalaryRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Request submitted",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TeacherSalaryRequestDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return TeacherSalaryRequest.objects.get(pk=pk)
        except TeacherSalaryRequest.DoesNotExist:
            return None

    def patch(self, request, pk):
        """Update request status (approve / reject)."""
        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "Request not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TeacherSalaryRequestSerializer(
            obj, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Request updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "Request not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        obj.delete()
        return Response(
            {"success": True, "message": "Request deleted"},
            status=status.HTTP_200_OK,
        )


# =====================================================================
# PENDING SALARY
# =====================================================================
class TeacherPendingSalaryListView(APIView):
    def get(self, request):
        qs = TeacherPendingSalary.objects.all().order_by("-id")

        teacher_id_card = request.query_params.get("teacher_id_card")
        if teacher_id_card:
            teacher = _get_teacher_by_card(teacher_id_card)
            if not teacher:
                return Response(
                    {"success": False, "message": "Teacher not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            qs = qs.filter(teacher=teacher)

        serializer = TeacherPendingSalarySerializer(qs, many=True)
        return Response(
            {"success": True, "count": qs.count(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )


# =====================================================================
# BANK DETAILS
# =====================================================================
class TeacherBankDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, teacher_id_card):
        teacher = _get_teacher_by_card(teacher_id_card)
        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            bank = TeacherBankDetail.objects.get(teacher=teacher)
        except TeacherBankDetail.DoesNotExist:
            return Response(
                {"success": False, "message": "Bank details not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"success": True, "data": TeacherBankDetailSerializer(bank).data},
            status=status.HTTP_200_OK,
        )

    def post(self, request, teacher_id_card):
        teacher = _get_teacher_by_card(teacher_id_card)
        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        bank = TeacherBankDetail.objects.filter(teacher=teacher).first()
        if bank:
            serializer = TeacherBankDetailSerializer(
                bank, data=request.data, partial=True
            )
        else:
            data = request.data.copy()
            data["teacher"] = teacher.id
            serializer = TeacherBankDetailSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Bank details saved",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )