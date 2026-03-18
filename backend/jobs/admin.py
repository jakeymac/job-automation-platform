from django.contrib import admin

from .models import Job, JobRun, JobFile


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


@admin.register(JobRun)
class JobRunAdmin(admin.ModelAdmin):
    list_display = (
        "job",
        "status",
        "exit_code",
        "started_at",
        "finished_at",
        "duration_seconds",
    )
    list_filter = ("status", "started_at", "finished_at")
    search_fields = ("job__name",)


@admin.register(JobFile)
class JobFileAdmin(admin.ModelAdmin):
    list_display = ("job", "file", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("job__name", "file")
