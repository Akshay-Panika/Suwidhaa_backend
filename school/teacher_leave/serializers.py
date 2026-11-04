from rest_framework import serializers
from .models import TeacherLeave


class TeacherLeaveSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    # ✅ Full teacher + school data
    teacher = serializers.SerializerMethodField()

    # ✅ Status validation field
    apply_status = serializers.ChoiceField(
        choices=TeacherLeave.STATUS_CHOICES,
        required=False,
        default='pending',
    )

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
            "teacher",
        ]
        read_only_fields = ["id", "created_date", "teacher"]

    def get_teacher(self, obj):
        if not obj.teacher_id_card:
            return None
        try:
            from school.teacher.models import Teacher
            from school.teacher.serializers import TeacherSerializer
        except Exception:
            return None

        teacher = Teacher.objects.filter(
            teacher_id_card=str(obj.teacher_id_card).strip()
        ).first()
        if not teacher:
            return None
        return TeacherSerializer(teacher).data

    def validate(self, attrs):
        # Date range validation
        start_date = attrs.get(
            "start_date", getattr(self.instance, "start_date", None)
        )
        end_date = attrs.get(
            "end_date", getattr(self.instance, "end_date", None)
        )
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be earlier than start date."}
            )

        # Status validation
        valid_statuses = [c[0] for c in TeacherLeave.STATUS_CHOICES]
        apply_status = attrs.get(
            "apply_status",
            getattr(self.instance, "apply_status", 'pending'),
        )
        if apply_status and apply_status not in valid_statuses:
            raise serializers.ValidationError({
                "apply_status":
                    f"Invalid status. Allowed: {valid_statuses}"
            })

        # Validate teacher exists
        teacher_id_card = attrs.get(
            "teacher_id_card",
            getattr(self.instance, "teacher_id_card", None)
        )
        if teacher_id_card:
            try:
                from school.teacher.models import Teacher
                teacher = Teacher.objects.filter(
                    teacher_id_card=str(teacher_id_card).strip()
                ).first()
                if not teacher:
                    raise serializers.ValidationError({
                        "teacher_id_card":
                            f"Teacher with ID card '{teacher_id_card}' not found"
                    })
            except serializers.ValidationError:
                raise
            except Exception:
                pass

        # Auto-fill teacher_id from teacher_id_card if missing
        if teacher_id_card and not attrs.get("teacher_id"):
            try:
                from school.teacher.models import Teacher
                teacher = Teacher.objects.filter(
                    teacher_id_card=str(teacher_id_card).strip()
                ).first()
                if teacher:
                    attrs["teacher_id"] = str(teacher.id)
            except Exception:
                pass

        return attrs