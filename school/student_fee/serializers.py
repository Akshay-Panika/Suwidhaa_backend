from rest_framework import serializers
from school.student.serializers import StudentSerializer
from school.student.models import Student
from .models import StudentFeeTransaction

class StudentFeeTransactionCreateSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), 
        source="student", 
        write_only=True
    )

    class Meta:
        model = StudentFeeTransaction
        fields = ['id', 'student_id', 'amount_paid', 'remarks', 'payment_date']
        read_only_fields = ['id', 'payment_date']

    def validate_amount_paid(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

class StudentFeeListSerializer(StudentSerializer):
    fee_summary = serializers.SerializerMethodField()

    class Meta(StudentSerializer.Meta):
        fields = list(StudentSerializer.Meta.fields)
        # fields = "__all__" ki jagah explicit list use karna padega agar __all__ hai toh
        if fields == "__all__":
            fields = [f.name for f in Student._meta.fields] + ['fee_summary']
        else:
            fields = fields + ['fee_summary']

    def get_fee_summary(self, obj):
        total_fee = float(obj.fee_amount) if obj.fee_amount else 0.0
        # Student model ke paid_amount field ko base rakh sakte hain
        paid_amount = float(obj.paid_amount) if obj.paid_amount else 0.0
        
        pending = total_fee - paid_amount
        if pending < 0: pending = 0.0

        status = "Paid" if pending == 0 and total_fee > 0 else "Pending"

        return {
            "total_fee": total_fee,
            "total_paid": paid_amount,
            "pending": pending,
            "status": status
        }

class StudentFeeTransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeeTransaction
        fields = ['id', 'amount_paid', 'remarks', 'payment_date']