from rest_framework import serializers
from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'subject_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_subject_name(self, value):
        value = value.strip()

        # Case-insensitive duplicate check
        queryset = Subject.objects.filter(subject_name__iexact=value)

        # Update ke waqt khud ko exclude karo
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "This subject already exists."
            )

        return value