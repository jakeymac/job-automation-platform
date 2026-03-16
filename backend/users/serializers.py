from django.contrib.auth import get_user_model
from rest_framework import serializers

from .validator_utils import (
    validate_email_util,
    validate_password_util,
    validate_username_util,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user
    def validate_username(self, value):
        is_valid, error_message = validate_username_util(value)
        if not is_valid:
            raise serializers.ValidationError(error_message)
        return value

    def validate_email(self, value):
        is_valid, error_message = validate_email_util(value)
        if not is_valid:
            raise serializers.ValidationError(error_message)
        return value

    def validate_password(self, value):
        is_valid, error_message = validate_password_util(value)
        if not is_valid:
            raise serializers.ValidationError(error_message)
        return value
