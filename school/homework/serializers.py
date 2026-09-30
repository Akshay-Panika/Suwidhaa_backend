from rest_framework import serializers
from .models import Homework, HomeworkStudent


class HomeworkStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkStudent
        fields = [
            'id',
            'student_id',
            'student_name',
            'student_class',
            'status',          # ⬅️ true / false
        ]
        read_only_fields = ['id']


class HomeworkSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)

    # ⬇️ REQUIRED students list — at least one student must be present
    students = HomeworkStudentSerializer(many=True, required=True, allow_empty=False)

    class Meta:
        model = Homework
        fields = [
            'id',
            'subject_name',
            'subject_topic',
            'issue_date',
            'end_date',
            'image',
            'class_name',
            'teacher_name',
            'teacher_id',
            'school_type',
            'students',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = instance.image.url if instance.image else None
        return data

    def validate(self, data):
        if data.get('end_date') and data.get('issue_date'):
            if data['end_date'] < data['issue_date']:
                raise serializers.ValidationError(
                    "End date cannot be before issue date"
                )
        return data

    def create(self, validated_data):
        students_data = validated_data.pop('students', [])
        homework = Homework.objects.create(**validated_data)
        for s in students_data:
            HomeworkStudent.objects.create(homework=homework, **s)
        return homework

    def update(self, instance, validated_data):
        students_data = validated_data.pop('students', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if students_data is not None:
            # Replace entire student list
            instance.students.all().delete()
            for s in students_data:
                HomeworkStudent.objects.create(homework=instance, **s)

        return instance