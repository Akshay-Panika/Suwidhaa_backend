from rest_framework import serializers
from .models import ReportCard


# ═══════════════════════════════════════════════════════════
# 📌 READ SERIALIZER
#    Returns full teacher + student model in response
# ═══════════════════════════════════════════════════════════
class ReportCardSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()   # ✅ full teacher model
    student = serializers.SerializerMethodField()   # ✅ full student model

    class Meta:
        model = ReportCard
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

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

    # ---------- full student ----------
    def get_student(self, obj):
        if not obj.student_id:
            return None
        try:
            sid = int(str(obj.student_id).strip())
        except (ValueError, TypeError):
            return None

        try:
            from school.student.models import Student
            from school.student.serializers import StudentSerializer
        except Exception:
            return None

        student = Student.objects.filter(id=sid).first()
        if not student:
            return None
        return StudentSerializer(student).data


# ═══════════════════════════════════════════════════════════
# 📌 CREATE / UPDATE SERIALIZER
#    Accepts teacher_id (id_card) + student_id (DB int id)
#    Validates existence in DB.
# ═══════════════════════════════════════════════════════════
class ReportCardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCard
        fields = [
            'teacher_id',
            'student_id',
            'class_name',
            'subject_name',
            'exam_name',
            'sujectmaks_marks',
            'pasingmaks_marks',
            'student_marks',
            'result',
            'description',
        ]

    # ── Validate teacher_id (id_card) ──
    def validate_teacher_id(self, value):
        if not value:
            raise serializers.ValidationError("teacher_id is required")

        try:
            from school.teacher.models import Teacher
            teacher = Teacher.objects.filter(
                teacher_id_card=str(value).strip()
            ).first()
            if not teacher:
                raise serializers.ValidationError(
                    f"Teacher with ID '{value}' not found"
                )
        except serializers.ValidationError:
            raise
        except Exception:
            pass
        return str(value).strip()

    # ── Validate student_id (DB integer id) ──
    def validate_student_id(self, value):
        if not value:
            raise serializers.ValidationError("student_id is required")

        try:
            sid = int(str(value).strip())
        except (ValueError, TypeError):
            raise serializers.ValidationError(
                f"student_id must be a valid integer (DB id), got '{value}'"
            )

        try:
            from school.student.models import Student
            if not Student.objects.filter(id=sid).exists():
                raise serializers.ValidationError(
                    f"Student with ID '{sid}' not found"
                )
        except serializers.ValidationError:
            raise
        except Exception:
            pass
        return str(sid)

    # ── Overall validation ──
    def validate(self, attrs):
        is_partial = bool(getattr(self, 'partial', False))

        # On create, all essential fields must be there
        if not is_partial:
            required = {
                'class_name': 'Class is required',
                'subject_name': 'Subject is required',
                'exam_name': 'Exam is required',
                'sujectmaks_marks': 'Total marks is required',
                'pasingmaks_marks': 'Passing marks is required',
                'student_marks': 'Student marks is required',
                'result': 'Result is required',
            }
            for f, msg in required.items():
                if attrs.get(f) in (None, ''):
                    raise serializers.ValidationError({f: msg})

        # Auto-compute result if not sent
        if ('student_marks' in attrs
                and 'pasingmaks_marks' in attrs
                and not attrs.get('result')):
            attrs['result'] = (
                'pass' if attrs['student_marks'] >= attrs['pasingmaks_marks']
                else 'fail'
            )

        return attrs