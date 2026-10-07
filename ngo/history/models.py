from django.db import models
from django.db.models.functions import Lower

from ngo.service.models import NgoService


class NgoHistory(models.Model):
    # 🔗 Core links
    service = models.ForeignKey(
        NgoService,
        on_delete=models.CASCADE,
        related_name="history",
    )

    # 👤 Donor ID (simple integer — no FK needed, works with external user IDs)
    donor_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="User/Donor ID from your auth system",
    )

    donate_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    # 🧾 Snapshot fields (auto-filled from service)
    service_name = models.CharField(max_length=255, blank=True, null=True)
    category_name = models.CharField(max_length=255, blank=True, null=True)
    service_image = models.URLField(blank=True, null=True)

    # 👤 Donor info
    donor_name = models.CharField(max_length=255, blank=True, null=True)
    donor_contact = models.CharField(max_length=15, blank=True, null=True)

    # 📝 Notes
    note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "NGO History"
        verbose_name_plural = "NGO History"
        indexes = [
            models.Index(fields=["donor_id", "-created_at"]),
            models.Index(fields=["service", "-created_at"]),
        ]

    def __str__(self):
        return f"History #{self.id} — {self.service_name} — ₹{self.donate_amount}"

    def save(self, *args, **kwargs):
        """
        Auto-fill service snapshot fields on save.
        """
        if self.service:
            self.service_name = self.service.name

            if self.service.category:
                self.category_name = self.service.category.name

            if self.service.images:
                self.service_image = (
                    self.service.images[0] if self.service.images else None
                )

        super().save(*args, **kwargs)