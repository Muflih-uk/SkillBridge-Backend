from django.urls import path

from .views import CurrentUserProfileView, LoginUserView, RegisterUserView

urlpatterns = [
    path("auth/register/", RegisterUserView.as_view(), name="register"),
    path("auth/login/", LoginUserView.as_view(), name="login"),
    path("profile/", CurrentUserProfileView.as_view(), name="current-user-profile"),
]
