from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    MILK_COLLECTION_OFFICER = "MILK_COLLECTION_OFFICER", "Milk Collection Officer"
    FARMER = "FARMER", "Farmer"


class User(AbstractUser):
    role = models.CharField(max_length=32, choices=Role.choices)
    mobile_number = models.CharField(max_length=15, blank=True, unique=False)

    def __str__(self):
        return f"{self.username} ({self.role})"
