from rest_framework import serializers
from school.teacher.serializers import TeacherSerializer

class TeacherSalaryListSerializer(TeacherSerializer):
    transaction = serializers.SerializerMethodField()

    class Meta(TeacherSerializer.Meta):
        fields = [f.name for f in TeacherSerializer.Meta.model._meta.fields] + ['transaction']

    def get_transaction(self, obj):
        return None