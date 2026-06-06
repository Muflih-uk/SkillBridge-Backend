import uuid

from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("learner", "Learner"),
        ("mentor", "Mentor"),
        ("admin", "Admin"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    avatar_url = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name


class MentorProfile(models.Model):
    id = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="mentor_profile",
    )
    experience_yrs = models.SmallIntegerField()
    availability = models.CharField(max_length=50, blank=True, null=True)
    linkedin_url = models.TextField(blank=True, null=True)
    ai_summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Mentor Profile for {self.id.display_name}"
