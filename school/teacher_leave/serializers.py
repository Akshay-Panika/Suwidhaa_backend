from rest_framework import serializers
from .models import TeacherLeave


class TeacherLeaveSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = TeacherLeave
        fields = [
            "id",
            "teacher_id",
            "teacher_id_card",
            "apply_status",
            "reason_msg",
            "start_date",
            "end_date",
            "image",
            "created_date",
        ]
        read_only_fields = ["id", "created_date"]

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be earlier than start date."}
            )
        return attrs