from django.apps import AppConfig


class EcommerceCategoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ecommerce.category"
    label = "ecommerce_category"   # unique label (banner conflict se bachne ke liye)