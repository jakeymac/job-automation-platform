import os

from django.conf import settings
from django.db import models


class Job(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    schedule = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    command = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=255, default="python:3.11-slim")

    timeout_seconds = models.IntegerField(default=300)
    allow_network = models.BooleanField(default=False)

    def __str__(self):
        return self.name


def job_file_upload_path(instance, filename):
    job_file_directory = os.path.join(settings.MEDIA_ROOT, "job_files", f"job_{instance.job.id}")
    return os.path.join(job_file_directory, filename)

def job_run_log_upload_path(instance):
    logs_directory = os.path.join(settings.MEDIA_ROOT, "job_logs")
    return os.path.join(logs_directory, f"job_run_{instance.id}.log")


class JobFile(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to=job_file_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        # delete the actual file first
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.job.name} - {self.file.name}"


class JobRun(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RUNNING = "RUNNING", "Running"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="runs")
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.PENDING
    )
    exit_code = models.IntegerField(blank=True, null=True)
    log_file = models.FileField(upload_to=job_run_log_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.FloatField(blank=True, null=True)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    trigger_type = models.CharField(
        max_length=50,
        choices=[("manual", "Manual"), ("scheduled", "Scheduled")],
        default="manual",
    )

    def __str__(self):
        return f"{self.job.name} - {self.get_status_display()} - {self.started_at}"
