from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "mobile_number", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Farm role", {"fields": ("role", "mobile_number")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Farm role", {"fields": ("role", "mobile_number")}),
    )
