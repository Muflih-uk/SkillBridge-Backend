from django.urls import path

from .views import (
    AvatarUploadView,
    CurrentUserProfileView,
    LoginUserView,
    RegisterUserView,
    TriggerMentorSummaryView,
)

urlpatterns = [
    path("auth/register/", RegisterUserView.as_view(), name="register"),
    path("auth/login/", LoginUserView.as_view(), name="login"),
    path("profile/", CurrentUserProfileView.as_view(), name="current-user-profile"),
    path("profile/avatar/", AvatarUploadView.as_view(), name="profile-avatar-upload"),
    path(
        "profile/generate-summary/",
        TriggerMentorSummaryView.as_view(),
        name="profile-ai-summary",
    ),
]
