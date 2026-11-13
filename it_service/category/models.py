from django.db import models, IntegrityError
from django.db.models.functions import Lower
from cloudinary.models import CloudinaryField


class ItServiceCategory(models.Model):
    # System Category Constants
    ALL_SERVICES_ID = 0
    ALL_SERVICES_NAME = "All"            # <-- CHANGED: was "All Services"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    image = CloudinaryField(
        "image",
        folder="suwidhaa/it_service/category",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "it_service_category"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_it_service_category_name_ci",
            ),
        ]

    @property
    def is_default(self) -> bool:
        return self.pk == self.ALL_SERVICES_ID

    # ------------------------------------------------------------------
    # Ensure the built-in "All" row exists (and its name is correct).
    # ------------------------------------------------------------------
    @classmethod
    def ensure_default(cls):
        # 1) If pk=0 exists but name is stale ("All Services"), rename it.
        cls.objects.filter(pk=cls.ALL_SERVICES_ID).exclude(
            name=cls.ALL_SERVICES_NAME
        ).update(name=cls.ALL_SERVICES_NAME)

        obj = cls.objects.filter(pk=cls.ALL_SERVICES_ID).first()
        if obj:
            return obj

        # 2) Create the row with pk=0.
        try:
            obj, _ = cls.objects.get_or_create(
                pk=cls.ALL_SERVICES_ID,
                defaults={"name": cls.ALL_SERVICES_NAME},
            )
            return obj
        except IntegrityError:
            # Row named "All" already exists at some other pk — use it.
            return cls.objects.filter(
                name__iexact=cls.ALL_SERVICES_NAME
            ).first()

    def save(self, *args, **kwargs):
        # Protect default category name
        if self.pk == self.ALL_SERVICES_ID:
            self.name = self.ALL_SERVICES_NAME
            if not type(self).objects.filter(pk=self.ALL_SERVICES_ID).exists():
                kwargs["force_insert"] = True
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_default:
            raise ValueError("The 'All' category cannot be deleted.")
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"IT Service Category {self.id} - {self.name}"