import hashlib
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

    NOTIFICATION_CHOICES = [
        ("ALL", "All job runs"),
        ("CUSTOM", "Only for custom notifications requested in job"),
        ("NONE", "No notifications"),
    ]
    notification_preference = models.CharField(
        max_length=20, choices=NOTIFICATION_CHOICES, default="ALL"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    command = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=255, default="python:3.11-slim")

    timeout_seconds = models.IntegerField(default=300)
    allow_network = models.BooleanField(default=False)

    def __str__(self):
        return self.name


def job_file_upload_path(instance, filename):
    return os.path.join("job_files", f"job_{instance.job.id}", filename)


def job_run_log_upload_path(instance):
    return os.path.join("job_logs", f"job_run_{instance.id}.log")


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

    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name="runs", db_index=True
    )
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.PENDING
    )
    exit_code = models.IntegerField(blank=True, null=True)
    log_file = models.FileField(
        upload_to=job_run_log_upload_path, blank=True, null=True
    )
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
    email_status = models.CharField(
        max_length=50,
        choices=[("PENDING", "Pending"), ("SENT", "Sent"), ("FAILED", "Failed"), ("NOT REQUESTED", "Not Requested")],
        default="PENDING",
    )
    email_sent_at = models.DateTimeField(blank=True, null=True)
    email_error = models.TextField(blank=True, null=True)
    custom_email_content = models.TextField(blank=True, null=True)

    state_snapshot = models.JSONField(
        blank=True, null=True
    )  # Store the state of the job at the time of execution (before the job run starts)
    updated_state = models.JSONField(
        blank=True, null=True
    )  # Updated state data after job execution

    api_token = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"{self.job.name} - {self.get_status_display()} - {self.started_at}"

    def set_api_token(self, token):
        self.api_token = hashlib.sha256(token.encode()).hexdigest()

    def check_api_token(self, token):
        if not self.api_token:
            return False
        return hashlib.sha256(token.encode()).hexdigest() == self.api_token


class JobState(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name="state")
    data = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job.name} State"
