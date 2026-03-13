from django.db import models
from django.conf import settings
class Job(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    schedule = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name