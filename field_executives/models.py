from django.conf import settings
from django.db import models


class FieldExecutiveStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"


class FieldExecutive(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="field_executive_profile",
    )
    employee_id = models.CharField(max_length=20, unique=True)
    assigned_area = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True)
    profile_photo = models.ImageField(
        upload_to="field-executives/photos/", blank=True, null=True
    )
    status = models.CharField(
        max_length=16,
        choices=FieldExecutiveStatus.choices,
        default=FieldExecutiveStatus.ACTIVE,
    )
    farmers_count = models.PositiveIntegerField(default=0)
    todays_collection_liters = models.PositiveIntegerField(default=0)
    joined_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-joined_date"]

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name() or self.user.username}"
