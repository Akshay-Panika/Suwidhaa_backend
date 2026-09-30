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
            "student_ids_list",
            "image",
            "teacher_id",
            "teacher_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except Exception:
                return str(obj.image)
        return None


class HomeworkCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Accepts student_ids_list as:
      [
        {"studentIdcard": "STU001", "status": false},
        {"studentIdcard": "STU002"}                 # status defaults to false
      ]

    Also tolerates:
      - Plain list of strings: ["STU001", "STU002"]
      - List of ints: [1, 2, 3]
      - Comma string: "STU001,STU002"
    All of these get normalized to list of dicts.
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
            "student_ids_list",
            "image",
            "teacher_id",
            "teacher_name",
        ]

    # ──────────────────────────────────────────────────────
    # Normalizer
    # ──────────────────────────────────────────────────────
    def _normalize_entry(self, entry):
        """
        Convert any entry to {"studentIdcard": "...", "status": false}
        """
        # If dict already → ensure keys exist
        if isinstance(entry, dict):
            card = (
                entry.get("studentIdcard")
                or entry.get("student_id_card")
                or entry.get("studentId")
                or entry.get("id")
                or ""
            )
            status = entry.get("status", False)
            return {
                "studentIdcard": str(card).strip(),
                "status": bool(status),
            }

        # If plain string/int → treat as studentIdcard
        if isinstance(entry, (str, int)):
            return {
                "studentIdcard": str(entry).strip(),
                "status": False,
            }

        raise serializers.ValidationError(
            f"Invalid student entry: {entry!r}"
        )

    def validate_student_ids_list(self, value):
        """
        Accept:
          - list of dicts / strings / ints
          - comma string
        Always return list of {"studentIdcard": str, "status": bool}
        """
        if value is None or value == "":
            return []

        # Case: comma string "STU001,STU002"
        if isinstance(value, str):
            value = [s.strip() for s in value.split(",") if s.strip()]

        if not isinstance(value, list):
            raise serializers.ValidationError(
                "student_ids_list must be a list or comma-separated string"
            )

        normalized = []
        for entry in value:
            obj = self._normalize_entry(entry)
            if obj["studentIdcard"]:  # skip empty cards
                normalized.append(obj)

        return normalized

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

        if not attrs.get("student_ids_list"):
            raise serializers.ValidationError(
                {"student_ids_list": "Select at least one student"}
            )

        return attrs