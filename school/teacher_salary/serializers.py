from rest_framework import serializers
from school.teacher.serializers import TeacherSerializer
from django.utils import timezone
from django.db.models import Sum
from .models import TeacherSalaryTransaction
from school.teacher.models import Teacher


class TeacherSalaryTransactionCreateSerializer(serializers.ModelSerializer):
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), 
        source="teacher", 
        write_only=True
    )

    class Meta:
        model = TeacherSalaryTransaction
        fields = ['id', 'teacher_id', 'amount_paid', 'month', 'year', 'remarks', 'payment_date']
        read_only_fields = ['id', 'payment_date']

    def validate(self, data):
        amount_paid = data.get('amount_paid')
        if amount_paid <= 0:
            raise serializers.ValidationError({"amount_paid": "Amount must be greater than 0."})
        return data


class TeacherSalaryListSerializer(TeacherSerializer):
    transaction = serializers.SerializerMethodField()

    class Meta(TeacherSerializer.Meta):
        fields = [f.name for f in TeacherSerializer.Meta.model._meta.fields] + ['transaction']

    def get_transaction(self, obj):
        today = timezone.now()
        current_month = today.month
        current_year = today.year

        base_salary = float(obj.salary) if obj.salary else 0.0

        paid_amount_query = TeacherSalaryTransaction.objects.filter(
            teacher=obj,
            month=current_month,
            year=current_year
        ).aggregate(total_paid=Sum('amount_paid'))
        
        paid_amount = float(paid_amount_query['total_paid'] or 0.0)
        pending_amount = base_salary - paid_amount

        if pending_amount < 0:
            pending_amount = 0.0

        return {
            "year": current_year,
            "month": current_month,
            "base_salary": base_salary,
            "total_paid": paid_amount,
            "pending": pending_amount,
            "status": "Paid" if pending_amount == 0 and paid_amount > 0 else "Pending"
        }