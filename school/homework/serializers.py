from rest_framework import serializers
from .models import Homework


# ═══════════════════════════════════════════════════════════
# 📌 READ SERIALIZER
#    Returns full teacher + students (model data) in response
# ═══════════════════════════════════════════════════════════
class HomeworkSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()   # ✅ full teacher model
    students = serializers.SerializerMethodField()  # ✅ full student models

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
            "students",        # ✅ NEW
            "image",
            "teacher_id",
            "teacher",         # ✅ NEW
            "teacher_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    # ---------- image url ----------
    def get_image(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except Exception:
                return str(obj.image)
        return None

    # ---------- full teacher ----------
    def get_teacher(self, obj):
        if not obj.teacher_id:
            return None
        try:
            from school.teacher.models import Teacher
            from school.teacher.serializers import TeacherSerializer
        except Exception:
            return None

        teacher = Teacher.objects.filter(
            teacher_id_card=str(obj.teacher_id).strip()
        ).first()
        if not teacher:
            return None
        return TeacherSerializer(teacher).data

    # ---------- full student models (order preserved) ----------
    def get_students(self, obj):
        if not obj.student_ids_list:
            return []

        try:
            from school.student.models import Student
            from school.student.serializers import StudentSerializer
        except Exception:
            return []

        # 1. Extract all studentIdcard values from JSON list
        card_ids = []
        for entry in obj.student_ids_list:
            if isinstance(entry, dict):
                card = (
                    entry.get("studentIdcard")
                    or entry.get("student_id_card")
                    or entry.get("studentId")
                    or ""
                )
                if card:
                    card_ids.append(str(card).strip())
            elif isinstance(entry, (str, int)):
                card_ids.append(str(entry).strip())

        if not card_ids:
            return []

        # 2. Fetch all students in ONE query
        students = Student.objects.filter(student_id_card__in=card_ids)
        student_map = {s.student_id_card: s for s in students}

        # 3. Preserve order from student_ids_list
        ordered = [student_map[cid] for cid in card_ids if cid in student_map]
        return StudentSerializer(ordered, many=True).data


# ═══════════════════════════════════════════════════════════
# 📌 CREATE / UPDATE SERIALIZER
#    teacher_id + studentIds only. teacher_name auto-filled.
# ═══════════════════════════════════════════════════════════
class HomeworkCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Request body (CREATE):
      {
        "school_type": "Primary",
        "class_name": "5A",
        "subject": "Math",
        "subject_topic": "Fractions",
        "issue_date": "2025-01-01",
        "end_date": "2025-01-05",
        "teacher_id": "TCH001",              <-- only teacher ID (id_card)
        "student_ids_list": [                 <-- only student IDs
            {"studentIdcard": "STU001", "status": false},
            {"studentIdcard": "STU002"}
        ]
      }

    Behavior:
      - teacher_name is auto-filled from Teacher model (do NOT send it).
      - Student entries can also be plain strings / ints / comma string.
      - All entries normalized to {"studentIdcard": str, "status": bool}
    """
    student_ids_list = serializers.JSONField(required=False)
    teacher_name = serializers.CharField(required=False, allow_blank=True)

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

    # ─────────────────────────────────────────────────────
    # Normalizer for individual entries
    # ─────────────────────────────────────────────────────
    def _normalize_entry(self, entry):
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

        if isinstance(entry, (str, int)):
            return {
                "studentIdcard": str(entry).strip(),
                "status": False,
            }

        raise serializers.ValidationError(
            f"Invalid student entry: {entry!r}"
        )

    def validate_student_ids_list(self, value):
        if value is None or value == "":
            return []

        # "STU001,STU002"
        if isinstance(value, str):
            value = [s.strip() for s in value.split(",") if s.strip()]

        if not isinstance(value, list):
            raise serializers.ValidationError(
                "student_ids_list must be a list or comma-separated string"
            )

        normalized = []
        for entry in value:
            obj = self._normalize_entry(entry)
            if obj["studentIdcard"]:
                normalized.append(obj)
        return normalized

    # ─────────────────────────────────────────────────────
    # Main validation
    # ─────────────────────────────────────────────────────
    def validate(self, attrs):
        is_partial = bool(getattr(self, "partial", False))

        # 1. Required fields ONLY on CREATE
        if not is_partial:
            required = {
                "class_name": "Class is required",
                "subject": "Subject is required",
                "subject_topic": "Subject topic is required",
                "issue_date": "Issue date is required",
                "end_date": "End date is required",
            }
            for f, msg in required.items():
                if not attrs.get(f):
                    raise serializers.ValidationError({f: msg})

        # 2. student_ids_list — must not be empty if provided
        if "student_ids_list" in attrs and not attrs["student_ids_list"]:
            raise serializers.ValidationError(
                {"student_ids_list": "Select at least one student"}
            )
        if not is_partial and not attrs.get("student_ids_list"):
            raise serializers.ValidationError(
                {"student_ids_list": "Select at least one student"}
            )

        # 3. teacher_id — required on create
        teacher_id = attrs.get("teacher_id")
        if teacher_id is None and self.instance is not None:
            teacher_id = self.instance.teacher_id

        if not is_partial and not teacher_id:
            raise serializers.ValidationError(
                {"teacher_id": "Teacher ID is required"}
            )

        # 4. Validate teacher exists + auto-fill teacher_name
        if teacher_id:
            try:
                from school.teacher.models import Teacher
                teacher = Teacher.objects.filter(
                    teacher_id_card=str(teacher_id).strip()
                ).first()
                if not teacher:
                    raise serializers.ValidationError(
                        {"teacher_id": f"Teacher with ID '{teacher_id}' not found"}
                    )
                # Always override teacher_name from Teacher model
                attrs["teacher_name"] = (
                    f"{teacher.first_name} {teacher.last_name}".strip()
                )
            except serializers.ValidationError:
                raise
            except Exception:
                pass  # soft-fail — don't break save

        # 5. Validate student IDs exist
        cards = [
            s["studentIdcard"]
            for s in attrs.get("student_ids_list", [])
            if isinstance(s, dict) and s.get("studentIdcard")
        ]
        if cards:
            try:
                from school.student.models import Student
                existing = set(
                    Student.objects.filter(student_id_card__in=cards)
                    .values_list("student_id_card", flat=True)
                )
                missing = [c for c in cards if c not in existing]
                if missing:
                    raise serializers.ValidationError({
                        "student_ids_list":
                            f"Students not found: {', '.join(missing)}"
                    })
            except serializers.ValidationError:
                raise
            except Exception:
                pass

        return attrs