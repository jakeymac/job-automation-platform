from django.db import models
from django.conf import settings


class Job(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    schedule = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class JobRun(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RUNNING = "RUNNING", "Running"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="runs")
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.PENDING
    )
    exit_code = models.IntegerField(blank=True, null=True)
    log_file = models.FileField(upload_to="job_logs/", blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
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
