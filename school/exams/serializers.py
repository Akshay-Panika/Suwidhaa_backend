from rest_framework import serializers
from .models import ClassExamTimetable, SubjectSchedule
from school.teacher.models import Teacher
from school.teacher.serializers import TeacherSerializer

class SubjectScheduleSerializer(serializers.ModelSerializer):
    # 👇 Read-only: Returns full teacher object
    invigilator_details = TeacherSerializer(source='invigilator', read_only=True)
    
    # 👇 Write-only: Accepts teacher ID to assign
    invigilator = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = SubjectSchedule
        fields = [
            'id',
            'subject',
            'date',
            'start_time',
            'end_time',
            'invigilator',           # Accepts ID
            'invigilator_details',   # Returns Teacher Object
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


class ClassExamTimetableSerializer(serializers.ModelSerializer):
    schedules = SubjectScheduleSerializer(many=True)
    exam_type_label = serializers.CharField(
        source='get_exam_type_display', read_only=True
    )
    school_name = serializers.CharField(source='school.school_name', read_only=True)

    class Meta:
        model = ClassExamTimetable
        fields = [
            'id',
            'school',
            'school_name',
            'class_name',
            'exam_type',
            'exam_type_label',
            'from_date',
            'to_date',
            'schedules',
            'created_by_id',
            'created_by_name',
            'created_at',
            'updated_at',
        ]
        extra_kwargs = {
            'created_by_id': {'required': False, 'allow_null': True, 'allow_blank': True},
            'created_by_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'school': {'required': False, 'allow_null': True},
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