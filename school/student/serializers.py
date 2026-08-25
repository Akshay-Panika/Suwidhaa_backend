from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    student_profile = serializers.FileField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Student
        fields = "__all__"

    def validate_student_id_card(self, value):
        """Validate that student_id_card is unique"""
        if value:
            # Check if the ID card already exists (excluding current instance if updating)
            instance = self.instance
            if instance:
                # For update operation
                if Student.objects.exclude(pk=instance.pk).filter(student_id_card=value).exists():
                    raise serializers.ValidationError("A student with this ID card number already exists.")
            else:
                # For create operation
                if Student.objects.filter(student_id_card=value).exists():
                    raise serializers.ValidationError("A student with this ID card number already exists.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.student_profile:
            data["student_profile"] = instance.student_profile.url
        else:
            data["student_profile"] = None

        return data