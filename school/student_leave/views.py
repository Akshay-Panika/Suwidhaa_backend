from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import StudentLeave
from .serializers import StudentLeaveSerializer, StudentLeaveApprovalSerializer
from school.student.models import Student


# ---------------- CREATE ----------------
class StudentLeaveCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        # Make mutable copy (important for multipart/QueryDict)
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)

        student_id_card = data.get("student_id_card")

        # ✅ Auto-fill details from Student (student-id-wise create)
        if student_id_card:
            try:
                student = (
                    Student.objects
                    .select_related("school")
                    .get(student_id_card=student_id_card)
                )
                if not data.get("student_name"):
                    data["student_name"] = f"{student.first_name} {student.last_name}"
                if not data.get("student_class"):
                    data["student_class"] = student.student_class or ""
                if student.school:
                    if not data.get("school_id"):
                        data["school_id"] = student.school.id
                    if not data.get("school_type"):
                        data["school_type"] = student.school.school_name
            except Student.DoesNotExist:
                # Let serializer validation report required-field errors
                pass

        serializer = StudentLeaveSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Leave applied successfully",
                    "data": serializer.data,
                },
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

        school_id = request.query_params.get("school_id")
        if school_id:
            leaves = leaves.filter(school_id=school_id)

        student_class = request.query_params.get("student_class")
        if student_class:
            leaves = leaves.filter(student_class=student_class)

        student_id_card = request.query_params.get("student_id_card")
        if student_id_card:
            leaves = leaves.filter(student_id_card=student_id_card)

        leave_status = request.query_params.get("leave_status")
        if leave_status:
            leaves = leaves.filter(leave_status=leave_status)

        serializer = StudentLeaveSerializer(leaves, many=True)
        return Response(
            {"status": True, "count": leaves.count(), "data": serializer.data},
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
            return Response(
                {"status": False, "message": "Leave not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"status": True, "data": StudentLeaveSerializer(leave).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response(
                {"status": False, "message": "Leave not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = StudentLeaveSerializer(leave, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": True, "message": "Leave updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response(
                {"status": False, "message": "Leave not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = StudentLeaveSerializer(leave, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": True, "message": "Leave updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response(
                {"status": False, "message": "Leave not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
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

        leave_status = request.query_params.get("leave_status")
        if leave_status:
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
    """GET /student-leave/list/school/<school_id>/?student_class=&leave_status="""

    def get(self, request, school_id):
        leaves = StudentLeave.objects.select_related("school").filter(school_id=school_id)

        student_class = request.query_params.get("student_class")
        if student_class:
            leaves = leaves.filter(student_class=student_class)

        leave_status = request.query_params.get("leave_status")
        if leave_status:
            leaves = leaves.filter(leave_status=leave_status)

        if not leaves.exists():
            return Response(
                {"status": False,
                 "message": f"No leaves found for school id '{school_id}'"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "status": True,
                "school_id": school_id,
                "count": leaves.count(),
                "data": StudentLeaveSerializer(leaves, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


# ---------------- BY CLASS ----------------
class StudentLeaveByClassView(APIView):
    """GET /student-leave/list/class/<student_class>/?school_id=&leave_status="""

    def get(self, request, student_class):
        leaves = StudentLeave.objects.select_related("school").filter(
            student_class=student_class
        )

        school_id = request.query_params.get("school_id")
        if school_id:
            leaves = leaves.filter(school_id=school_id)

        leave_status = request.query_params.get("leave_status")
        if leave_status:
            leaves = leaves.filter(leave_status=leave_status)

        if not leaves.exists():
            return Response(
                {"status": False,
                 "message": f"No leaves found for class '{student_class}'"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "status": True,
                "student_class": student_class,
                "count": leaves.count(),
                "data": StudentLeaveSerializer(leaves, many=True).data,
            },
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
            return Response(
                {"status": False, "message": "Leave not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = StudentLeaveApprovalSerializer(leave, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": f"Leave {serializer.validated_data.get('leave_status')} successfully",
                    "data": StudentLeaveSerializer(leave).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )