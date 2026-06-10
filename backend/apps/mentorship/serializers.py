from rest_framework import serializers

from apps.users.serializers import UserProfileSerializer

from .models import AIMatchResult, LearningPath, MentorshipRequest


class MentorshipRequestSerializer(serializers.ModelSerializer):
    learner_details = UserProfileSerializer(source="learner", read_only=True)
    mentor_details = UserProfileSerializer(source="mentor", read_only=True)

    class Meta:
        model = MentorshipRequest
        fields = [
            "id",
            "learner",
            "learner_details",
            "mentor",
            "mentor_details",
            "status",
            "message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "learner", "status", "created_at", "updated_at"]


class LearningPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPath
        fields = ["id", "user", "goal", "title", "content", "created_at"]
        read_only_fields = ["id", "user", "title", "content", "created_at"]


class AIMatchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMatchResult
        fields = ["id", "learner", "goal", "results", "created_at"]
        read_only_fields = ["id", "learner", "results", "created_at"]
