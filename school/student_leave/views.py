from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import StudentLeave
from .serializers import StudentLeaveSerializer, StudentLeaveApprovalSerializer
from school.student.models import Student


# ─────────────────────────────────────────────
# Helper: derive leave fields from Student
# ─────────────────────────────────────────────
def _get_student_extra(student_id_card):
    """Return (student, extra_fields_dict) or (None, None)."""
    if not student_id_card:
        return None, None
    try:
        student = Student.objects.select_related("school").get(
            student_id_card=student_id_card
        )
    except Student.DoesNotExist:
        return None, None

    extra = {
        "student_name": f"{student.first_name} {student.last_name}".strip(),
        "student_class": student.student_class or "",
        "school": student.school,
        "school_type": student.school.school_name if student.school else "",
    }
    return student, extra


# ---------------- CREATE ----------------
class StudentLeaveCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        card = data.get("student_id_card")

        if not card:
            return Response(
                {"status": False, "errors": {"student_id_card": ["This field is required."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        student, extra = _get_student_extra(card)
        if not student:
            return Response(
                {"status": False,
                 "errors": {"student_id_card": [f"Student with ID card '{card}' not found."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StudentLeaveSerializer(data=data)
        if serializer.is_valid():
            serializer.save(**extra)
            return Response(
                {"status": True, "message": "Leave applied successfully",
                 "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ---------------- LIST (with query filters) ----------------
class StudentLeaveListView(APIView):
    def get(self, request):
        leaves = StudentLeave.objects.select_related("school").all()

        if school_id := request.query_params.get("school_id"):
            leaves = leaves.filter(school_id=school_id)
        if student_class := request.query_params.get("student_class"):
            leaves = leaves.filter(student_class=student_class)
        if card := request.query_params.get("student_id_card"):
            leaves = leaves.filter(student_id_card=card)
        if leave_status := request.query_params.get("leave_status"):
            leaves = leaves.filter(leave_status=leave_status)

        return Response(
            {"status": True, "count": leaves.count(),
             "data": StudentLeaveSerializer(leaves, many=True).data},
            status=status.HTTP_200_OK,
        )


# ---------------- DETAIL ----------------
class StudentLeaveDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return StudentLeave.objects.get(pk=pk)
        except StudentLeave.DoesNotExist:
            return None

    def get(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response({"status": False, "message": "Leave not found"},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(
            {"status": True, "data": StudentLeaveSerializer(leave).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response({"status": False, "message": "Leave not found"},
                            status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        card = data.get("student_id_card", leave.student_id_card)

        student, extra = _get_student_extra(card)
        if not student:
            return Response(
                {"status": False,
                 "errors": {"student_id_card": [f"Student with ID card '{card}' not found."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StudentLeaveSerializer(leave, data=data)
        if serializer.is_valid():
            serializer.save(**extra)
            return Response(
                {"status": True, "message": "Leave updated",
                 "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response({"status": False, "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response({"status": False, "message": "Leave not found"},
                            status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        card = data.get("student_id_card", leave.student_id_card)

        student, extra = _get_student_extra(card)
        if not student:
            return Response(
                {"status": False,
                 "errors": {"student_id_card": [f"Student with ID card '{card}' not found."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StudentLeaveSerializer(leave, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(**extra)
            return Response(
                {"status": True, "message": "Leave updated",
                 "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response({"status": False, "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response({"status": False, "message": "Leave not found"},
                            status=status.HTTP_404_NOT_FOUND)
        leave.delete()
        return Response(
            {"status": True, "message": "Leave deleted successfully"},
            status=status.HTTP_200_OK,
        )


# ---------------- BY STUDENT ID CARD ----------------
class StudentLeaveByIdCardView(APIView):
    def get(self, request, student_id_card):
        leaves = StudentLeave.objects.select_related("school").filter(
            student_id_card=student_id_card
        )
        if leave_status := request.query_params.get("leave_status"):
            leaves = leaves.filter(leave_status=leave_status)

        if not leaves.exists():
            return Response(
                {"status": False, "message": "No leaves found for this student id card"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"status": True, "count": leaves.count(),
             "data": StudentLeaveSerializer(leaves, many=True).data},
            status=status.HTTP_200_OK,
        )


# ---------------- BY SCHOOL ID ----------------
class StudentLeaveBySchoolView(APIView):
    def get(self, request, school_id):
        leaves = StudentLeave.objects.select_related("school").filter(school_id=school_id)
        if sc := request.query_params.get("student_class"):
            leaves = leaves.filter(student_class=sc)
        if st := request.query_params.get("leave_status"):
            leaves = leaves.filter(leave_status=st)

        if not leaves.exists():
            return Response(
                {"status": False,
                 "message": f"No leaves found for school id '{school_id}'"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"status": True, "school_id": school_id, "count": leaves.count(),
             "data": StudentLeaveSerializer(leaves, many=True).data},
            status=status.HTTP_200_OK,
        )


# ---------------- BY CLASS ----------------
class StudentLeaveByClassView(APIView):
    def get(self, request, student_class):
        leaves = StudentLeave.objects.select_related("school").filter(
            student_class=student_class
        )
        if sid := request.query_params.get("school_id"):
            leaves = leaves.filter(school_id=sid)
        if st := request.query_params.get("leave_status"):
            leaves = leaves.filter(leave_status=st)

        if not leaves.exists():
            return Response(
                {"status": False,
                 "message": f"No leaves found for class '{student_class}'"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"status": True, "student_class": student_class,
             "count": leaves.count(),
             "data": StudentLeaveSerializer(leaves, many=True).data},
            status=status.HTTP_200_OK,
        )


# ---------------- TEACHER APPROVAL ----------------
class StudentLeaveApprovalView(APIView):
    def get_object(self, pk):
        try:
            return StudentLeave.objects.get(pk=pk)
        except StudentLeave.DoesNotExist:
            return None

    def patch(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response({"status": False, "message": "Leave not found"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = StudentLeaveApprovalSerializer(leave, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": f"Leave {leave.leave_status} successfully",
                    "data": StudentLeaveSerializer(leave).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response({"status": False, "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)