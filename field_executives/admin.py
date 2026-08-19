from django.contrib import admin

from field_executives.models import FieldExecutive


@admin.register(FieldExecutive)
class FieldExecutiveAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "user",
        "assigned_area",
        "status",
        "farmers_count",
        "joined_date",
    )
    list_filter = ("status", "assigned_area")
    search_fields = ("employee_id", "user__username", "user__first_name", "user__last_name")
