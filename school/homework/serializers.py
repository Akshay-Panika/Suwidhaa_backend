from rest_framework import serializers
from .models import Homework


class HomeworkSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Homework
        fields = [
            "id",
            "school_type",
            "class_name",
            "subject",
            "subject_topic",
            "issue_date",
            "end_date",
            "student_ids_list",     # ✅ JSON list directly
            "image",
            "teacher_id",
            "teacher_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    # ✅ Return full Cloudinary URL
    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except Exception:
                return str(obj.image)
        return None


class HomeworkCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Used for POST (create) and PUT/PATCH (update).
    Accepts student_ids_list as either:
      - List: ["1", "2", "3"]   ✅ preferred
      - Comma string: "1,2,3"   ✅ tolerated for convenience
    Image is uploaded as multipart/form-data.
    """
    student_ids_list = serializers.JSONField(required=False)

    class Meta:
        model = Homework
        fields = [
            "school_type",
            "class_name",
            "subject",
            "subject_topic",
            "issue_date",
            "end_date",
            "student_ids_list",     # ✅ only this field now
            "image",
            "teacher_id",
            "teacher_name",
        ]

    def validate_student_ids_list(self, value):
        """
        Normalize student_ids_list to always be a list of strings.
        Accepts: ["1","2"] or "1,2,3" or None
        """
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str):
            return [s.strip() for s in value.split(",") if s.strip()]
        raise serializers.ValidationError(
            "student_ids_list must be a list or comma-separated string"
        )

    def validate(self, attrs):
        if not attrs.get("class_name"):
            raise serializers.ValidationError({"class_name": "Class is required"})
        if not attrs.get("subject"):
            raise serializers.ValidationError({"subject": "Subject is required"})
        if not attrs.get("subject_topic"):
            raise serializers.ValidationError(
                {"subject_topic": "Subject topic is required"}
            )
        if not attrs.get("issue_date"):
            raise serializers.ValidationError(
                {"issue_date": "Issue date is required"}
            )
        if not attrs.get("end_date"):
            raise serializers.ValidationError({"end_date": "End date is required"})

        # Optional: enforce at least one student
        if not attrs.get("student_ids_list"):
            raise serializers.ValidationError(
                {"student_ids_list": "Select at least one student"}
            )
        return attrs