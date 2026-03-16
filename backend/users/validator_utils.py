from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

User = get_user_model()


def validate_username(username):
    """Validates that the username is at least 6 characters long, contains no spaces, and is not already taken.
    Returns a tuple of (is_valid, error_message). If is_valid is True, error_message will be an empty string.
    """
    if len(username) < 6 or " " in username:
        return (
            False,
            "Username must be at least 6 characters long and contain no spaces",
        )

    if User.objects.filter(username=username).exists():
        return False, "Username is already taken"

    return True, ""


def validate_email(email):
    """Validates that the email is in a valid format and is not already taken.
    Returns a tuple of (is_valid, error_message). If is_valid is True, error_message will be an empty string.
    """
    try:
        validate_email(email)
    except ValidationError:
        return False, "Invalid email format"

    if User.objects.filter(email=email).exists():
        return False, "Email is already taken"

    return True, ""


def validate_password(password):
    """Validates that the password is at least 8 characters long and contains at least one number and one special character.
    Returns a tuple of (is_valid, error_message). If is_valid is True, error_message will be an empty string.
    """
    if len(password) < 8 or " " in password:
        return (
            False,
            "Password must be at least 8 characters long and contain no spaces",
        )

    return True, ""
