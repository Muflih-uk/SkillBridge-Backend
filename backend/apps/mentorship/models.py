import uuid

from django.db import models

from apps.users.models import UserProfile


class MentorshipRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learner = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="sent_requests"
    )
    mentor = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="received_requests"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LearningPath(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="learning_paths"
    )
    goal = models.TextField()
    title = models.CharField(max_length=200)
    content = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class AIMatchResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learner = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="match_results"
    )
    goal = models.TextField()
    results = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
