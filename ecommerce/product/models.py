from django.db import models
from cloudinary.models import CloudinaryField
from ecommerce.subcategory.models import EcommerceSubcategory
from auth.app_auth.models import User


class EcommerceProduct(models.Model):
    subcategory = models.ForeignKey(
        EcommerceSubcategory,
        on_delete=models.CASCADE,
        related_name="products",
        db_index=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="products",
        db_index=True,
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    stock = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_product"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.title} (ID: {self.id})"

    @property
    def primary_image(self):
        first = self.images.first()
        return first.image.url if first and first.image else None


class EcommerceProductImage(models.Model):
    product = models.ForeignKey(
        EcommerceProduct,
        on_delete=models.CASCADE,
        related_name="images",
        db_index=True,
    )
    image = CloudinaryField(
        "image",
        folder="suwidhaa/ecommerce/product",
        blank=False,
        null=False,
    )

    class Meta:
        db_table = "ecommerce_product_image"
        ordering = ["id"]

    def __str__(self):
        return f"Image {self.id} for Product {self.product_id}"


class EcommerceFavorite(models.Model):
    """Per-user favorites table."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        db_index=True,
    )
    product = models.ForeignKey(
        EcommerceProduct,
        on_delete=models.CASCADE,
        related_name="favorites",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ecommerce_favorite"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_favorite",
            )
        ]

    def __str__(self):
        return f"User {self.user_id} ♥ Product {self.product_id}"


class EcommerceCart(models.Model):
    """Per-user cart table. Each row = one product in a user's cart."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_items",
        db_index=True,
    )
    product = models.ForeignKey(
        EcommerceProduct,
        on_delete=models.CASCADE,
        related_name="cart_items",
        db_index=True,
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_cart"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_cart",
            )
        ]

    def __str__(self):
        return f"User {self.user_id} 🛒 Product {self.product_id} x{self.quantity}"