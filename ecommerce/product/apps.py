from django.apps import AppConfig


class EcommerceProductConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ecommerce.product"
    label = "ecommerce_product"   # unique label