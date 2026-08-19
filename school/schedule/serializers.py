from rest_framework import serializers
from .models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    banner_image = serializers.FileField(
        required=False,
        allow_null=True,
    )
    pdf_file = serializers.FileField(
        required=False,
        allow_null=True,
    )
    
    class Meta:
        model = Schedule
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if instance.banner_image:
            data["banner_image"] = instance.banner_image.url
        else:
            data["banner_image"] = None
            
        if instance.pdf_file:
            data["pdf_file"] = instance.pdf_file.url
        else:
            data["pdf_file"] = None
            
        return data