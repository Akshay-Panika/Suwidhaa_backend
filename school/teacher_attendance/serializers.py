from rest_framework import serializers
from .models import TeacherAttendance


class TeacherAttendanceSerializer(serializers.ModelSerializer):
    teacher_id = serializers.IntegerField(source='teacher.id', read_only=True)
    working_hours = serializers.ReadOnlyField()
    check_in_time = serializers.DateTimeField(format="%I:%M %p", read_only=True)
    check_out_time = serializers.DateTimeField(format="%I:%M %p", read_only=True)
    date = serializers.DateField(format="%Y-%m-%d", read_only=True)
    day_name = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()

    class Meta:
        model = TeacherAttendance
        fields = [
            'id',
            'teacher_id',
            'date',
            'day_name',
            'month',
            'year',
            'check_in_time',
            'check_out_time',
            'status',
            'working_hours',
            'remarks',
        ]

    def get_day_name(self, obj):
        return obj.date.strftime("%A")

    def get_month(self, obj):
        return obj.date.strftime("%B")

    def get_year(self, obj):
        return obj.date.year