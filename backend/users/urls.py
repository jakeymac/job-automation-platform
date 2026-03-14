from django.urls import path
from .endpoints import RegisterUserView

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
]