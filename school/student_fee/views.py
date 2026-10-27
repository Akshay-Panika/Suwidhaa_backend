from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from school.student.models import Student
from .models import StudentFeeTransaction
from .serializers import (
    StudentFeeListSerializer, 
    StudentFeeTransactionCreateSerializer,
    StudentFeeTransactionHistorySerializer
)

class StudentFeeListView(APIView):
    def get(self, request):
        students = Student.objects.select_related("school").all().order_by("-id")
        serializer = StudentFeeListSerializer(students, many=True)
        return Response({"success": True, "count": students.count(), "data": serializer.data})

class StudentFeeBySchoolView(APIView):
    def get(self, request, school_id):
        students = Student.objects.filter(school_id=school_id).select_related("school").order_by("-id")
        if not students.exists():
            return Response({"success": False, "message": "No students found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudentFeeListSerializer(students, many=True)
        return Response({"success": True, "school_id": school_id, "count": students.count(), "data": serializer.data})

class StudentFeeTransactionCreateView(APIView):
    def post(self, request):
        serializer = StudentFeeTransactionCreateSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                fee_tx = serializer.save()
                # Student ke total paid_amount me add karein
                student = fee_tx.student
                student.paid_amount = float(student.paid_amount) + float(fee_tx.amount_paid)
                student.save()
                
            return Response({"success": True, "message": "Fee recorded", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class StudentFeeTransactionHistoryView(APIView):
    def get(self, request, student_id):
        transactions = StudentFeeTransaction.objects.filter(student_id=student_id).order_by('-payment_date')
        serializer = StudentFeeTransactionHistorySerializer(transactions, many=True)
        return Response({"success": True, "count": transactions.count(), "data": serializer.data})

class StudentFeeTransactionDeleteView(APIView):
    def delete(self, request, student_id, transaction_id):
        try:
            with transaction.atomic():
                tx = StudentFeeTransaction.objects.get(id=transaction_id, student_id=student_id)
                student = tx.student
                # Delete karne par amount wapas minus karein
                student.paid_amount = max(0, float(student.paid_amount) - float(tx.amount_paid))
                student.save()
                tx.delete()
            return Response({"success": True, "message": "Transaction deleted"})
        except StudentFeeTransaction.DoesNotExist:
            return Response({"success": False, "message": "Not found"}, status=status.HTTP_404_NOT_FOUND)