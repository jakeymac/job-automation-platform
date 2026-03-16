from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "schedule",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("owner", "is_active", "created_at")
    search_fields = ("name", "description")
