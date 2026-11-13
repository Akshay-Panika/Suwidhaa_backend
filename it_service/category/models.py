import logging

from django.db import models, IntegrityError
from django.db.models.functions import Lower
from cloudinary.models import CloudinaryField

logger = logging.getLogger(__name__)


class ItServiceCategory(models.Model):
    ALL_SERVICES_ID = 0
    ALL_SERVICES_NAME = "All"

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
    # Robust: guarantees the pk=0 "All" row exists
    # ------------------------------------------------------------------
    @classmethod
    def ensure_default(cls):
        default_id = cls.ALL_SERVICES_ID
        default_name = cls.ALL_SERVICES_NAME

        # 1) Fix a stale name ("All Services" → "All") on the pk=0 row
        try:
            cls.objects.filter(pk=default_id).exclude(name=default_name).update(
                name=default_name
            )
        except Exception:
            logger.exception("ensure_default: rename step failed")

        # 2) Return if it already exists
        obj = cls.objects.filter(pk=default_id).first()
        if obj:
            return obj

        # 3) Create with bulk_create — bypasses save() and forces id=0
        try:
            cls.objects.bulk_create(
                [cls(id=default_id, name=default_name)],
                ignore_conflicts=True,
            )
        except Exception:
            logger.exception("ensure_default: bulk_create failed")

        # 4) Verify
        obj = cls.objects.filter(pk=default_id).first()
        if obj:
            return obj

        # 5) Last resort
        try:
            obj, _ = cls.objects.get_or_create(
                pk=default_id, defaults={"name": default_name}
            )
            return obj
        except IntegrityError:
            # A row named "All" exists at some other pk — use it
            return cls.objects.filter(name__iexact=default_name).first()
        except Exception:
            logger.exception("ensure_default: get_or_create failed")
            return None

    def save(self, *args, **kwargs):
        # Protect the default row's name
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