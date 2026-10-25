from django.db import models
from school.school_type.models import SchoolType

class Subject(models.Model):
    # ✅ School FK (school id wise create)
    school = models.ForeignKey(
        SchoolType,
        on_delete=models.CASCADE,
        related_name="subjects",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]
        # ✅ Ek school me ek subject ka naam ek hi baar ho sakta hai
        unique_together = ("name", "school")

    def __str__(self):
        school_name = self.school.school_name if self.school else "No school"
        return f"{self.name} ({school_name})"