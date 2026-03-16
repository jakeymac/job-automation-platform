from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"

    def validate_schedule(self, value):
        from .utils import validate_cron_schedule

        if not validate_cron_schedule(value):
            raise serializers.ValidationError("Invalid cron schedule format")
        return value
