from django.urls import path

from .views import (
    AIMatchResultDetailView,
    AIMentorMatchView,
    LearningPathDetailView,
    MentorshipRequestActionView,
    MentorshipRequestListCreateView,
    TriggerLearningPathView,
)

urlpatterns = [
    path(
        "requests/",
        MentorshipRequestListCreateView.as_view(),
        name="requests-list-create",
    ),
    path(
        "requests/<uuid:pk>/action/",
        MentorshipRequestActionView.as_view(),
        name="request-resolution-action",
    ),
    path(
        "ai/generate-path/",
        TriggerLearningPathView.as_view(),
        name="ai-generate-learning-path",
    ),
    path("ai/match-mentors/", AIMentorMatchView.as_view(), name="ai-match-mentors"),
    path(
        "learning-paths/<uuid:pk>/",
        LearningPathDetailView.as_view(),
        name="learning-path-detail",
    ),
    path(
        "ai/match-results/<uuid:pk>/",
        AIMatchResultDetailView.as_view(),
        name="ai-match-results-detail",
    ),
]
