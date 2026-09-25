from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import StudentLeave
from .serializers import StudentLeaveSerializer, StudentLeaveApprovalSerializer


class StudentLeaveCreateView(APIView):

    def post(self, request):
        serializer = StudentLeaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": True, "message": "Leave applied successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class StudentLeaveListView(APIView):

    def get(self, request):
        leaves = StudentLeave.objects.all()
        serializer = StudentLeaveSerializer(leaves, many=True)
        return Response(
            {"status": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class StudentLeaveDetailView(APIView):

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
        serializer = StudentLeaveSerializer(leave)
        return Response(
            {"status": True, "data": serializer.data},
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


class StudentLeaveByIdCardView(APIView):

    def get(self, request, student_id_card):
        leaves = StudentLeave.objects.filter(student_id_card=student_id_card)
        if not leaves.exists():
            return Response(
                {"status": False, "message": "No leaves found for this student id card"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = StudentLeaveSerializer(leaves, many=True)
        return Response(
            {"status": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )


# ---------- NEW: Teacher Approval API ----------
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