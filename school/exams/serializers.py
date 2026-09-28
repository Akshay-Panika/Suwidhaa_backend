# school/exams/serializers.py
from rest_framework import serializers

from .models import ClassExamTimetable, SubjectSchedule


# ==================== SUBJECT SCHEDULE ====================
class SubjectScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectSchedule
        fields = [
            'id',
            'subject',
            'date',
            'start_time',
            'end_time',
            'invigilator',
            'room',
        ]

    def validate(self, attrs):
        start = attrs.get('start_time')
        end = attrs.get('end_time')
        if start and end and start >= end:
            raise serializers.ValidationError(
                {'end_time': 'End time must be after start time.'}
            )
        return attrs


# ==================== CLASS EXAM TIMETABLE ====================
class ClassExamTimetableSerializer(serializers.ModelSerializer):
    schedules = SubjectScheduleSerializer(many=True)
    exam_type_label = serializers.CharField(
        source='get_exam_type_display', read_only=True
    )

    class Meta:
        model = ClassExamTimetable
        fields = [
            'id',
            'class_name',
            'exam_type',
            'exam_type_label',
            'from_date',
            'to_date',
            'schedules',
            'created_by_id',      # optional int
            'created_by_name',    # optional string
            'created_at',
            'updated_at',
        ]
        extra_kwargs = {
            'created_by_id': {'required': False, 'allow_null': True},
            'created_by_name': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        from_date = attrs.get('from_date')
        to_date = attrs.get('to_date')
        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError(
                {'to_date': 'To date must be on or after from date.'}
            )
        return attrs

    def create(self, validated_data):
        schedules_data = validated_data.pop('schedules', [])
        timetable = ClassExamTimetable.objects.create(**validated_data)

        SubjectSchedule.objects.bulk_create([
            SubjectSchedule(timetable=timetable, **s) for s in schedules_data
        ])

        return timetable

    def update(self, instance, validated_data):
        schedules_data = validated_data.pop('schedules', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if schedules_data is not None:
            instance.schedules.all().delete()
            SubjectSchedule.objects.bulk_create([
                SubjectSchedule(timetable=instance, **s)
                for s in schedules_data
            ])

        return instance