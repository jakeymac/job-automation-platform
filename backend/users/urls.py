from django.urls import path

from .endpoints import IsEmailValidView, IsUsernameValidView, RegisterUserView

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("username-valid/", IsUsernameValidView.as_view(), name="check-username"),
    path("email-valid/", IsEmailValidView.as_view(), name="check-email"),
]
