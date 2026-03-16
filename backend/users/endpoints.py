from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer
from .validator_utils import validate_email_util, validate_username_util

User = get_user_model()


class RegisterUserView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IsUsernameValidView(APIView):
    """Checks if a username is valid and not already taken.
    Requirements: - must be at least 6 characters long with no spaces
    """

    permission_classes = []

    def get(self, request):
        username = request.query_params.get("username")
        if not username:
            return Response(
                {"error": "Username query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_valid, error_message = validate_username_util(username)

        if not is_valid:
            return Response(
                {"valid": False, "error": error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"valid": True})


class IsEmailValidView(APIView):
    """Checks if an email is valid and not already taken."""

    permission_classes = []

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response(
                {"error": "Email query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_valid, error_message = validate_email_util(email)

        if not is_valid:
            return Response(
                {"valid": False, "error": error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"valid": True})
