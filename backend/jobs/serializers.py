from rest_framework import serializers

from .models import Job, JobRun


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"

    def validate_schedule(self, value):
        from .utils import validate_job_schedule

        valid = validate_job_schedule(value)

        if not valid["valid"]:
            raise serializers.ValidationError("Invalid cron schedule format: " + valid["error"])
        return value

class JobRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRun
        fields = "__all__"