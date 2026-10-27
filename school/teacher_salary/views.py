from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from school.teacher.models import Teacher
from .models import TeacherSalaryTransaction
from .serializers import (
    TeacherSalaryListSerializer, 
    TeacherSalaryTransactionCreateSerializer,
    TeacherSalaryTransactionUpdateSerializer,
    TeacherSalaryTransactionHistorySerializer
)


class TeacherSalaryListView(APIView):
    def get(self, request):
        teachers = Teacher.objects.select_related("school").all().order_by("-id")
        serializer = TeacherSalaryListSerializer(teachers, many=True)

        return Response(
            {
                "success": True,
                "count": teachers.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class TeacherSalaryBySchoolView(APIView):
    def get(self, request, school_id):
        teachers = Teacher.objects.filter(school_id=school_id).select_related("school").order_by("-id")
        
        if not teachers.exists():
            return Response(
                {
                    "success": False, 
                    "message": f"No teachers found for school id '{school_id}'"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TeacherSalaryListSerializer(teachers, many=True)

        return Response(
            {
                "success": True,
                "school_id": school_id,
                "count": teachers.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class TeacherSalaryTransactionCreateView(APIView):
    def post(self, request):
        serializer = TeacherSalaryTransactionCreateSerializer(data=request.data)

        if serializer.is_valid():
            transaction = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Salary transaction recorded successfully",
                    "data": TeacherSalaryTransactionCreateSerializer(transaction).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class TeacherSalaryTransactionDetailView(APIView):
    def get_object(self, teacher_id, transaction_id):
        try:
            return TeacherSalaryTransaction.objects.get(id=transaction_id, teacher_id=teacher_id)
        except TeacherSalaryTransaction.DoesNotExist:
            return None

    def put(self, request, teacher_id, transaction_id):
        transaction = self.get_object(teacher_id, transaction_id)
        
        if not transaction:
            return Response(
                {"success": False, "message": "Transaction not found for this teacher"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TeacherSalaryTransactionUpdateSerializer(transaction, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Transaction updated successfully",
                    "data": TeacherSalaryTransactionCreateSerializer(transaction).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, teacher_id, transaction_id):
        transaction = self.get_object(teacher_id, transaction_id)
        
        if not transaction:
            return Response(
                {"success": False, "message": "Transaction not found for this teacher"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TeacherSalaryTransactionUpdateSerializer(transaction, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Transaction updated successfully",
                    "data": TeacherSalaryTransactionCreateSerializer(transaction).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, teacher_id, transaction_id):
        transaction = self.get_object(teacher_id, transaction_id)
        
        if not transaction:
            return Response(
                {"success": False, "message": "Transaction not found for this teacher"},
                status=status.HTTP_404_NOT_FOUND,
            )

        transaction.delete()
        return Response(
            {"success": True, "message": "Transaction deleted successfully"},
            status=status.HTTP_200_OK,
        )


class TeacherTransactionHistoryView(APIView):
    def get(self, request, teacher_id):
        transactions = TeacherSalaryTransaction.objects.filter(
            teacher_id=teacher_id
        ).order_by('-year', '-month', '-payment_date')
        
        if not transactions.exists():
            return Response(
                {
                    "success": True, 
                    "message": "No transactions found for this teacher",
                    "count": 0,
                    "total_paid_all_time": 0.0,
                    "data": []
                },
                status=status.HTTP_200_OK,
            )
            
        serializer = TeacherSalaryTransactionHistorySerializer(transactions, many=True)
        total_paid = transactions.aggregate(total=Sum('amount_paid'))['total'] or 0.0
        
        return Response(
            {
                "success": True,
                "teacher_id": teacher_id,
                "count": transactions.count(),
                "total_paid_all_time": total_paid,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )