from rest_framework import serializers

from apps.users.serializers import UserProfileSerializer

from .models import Skill


class SkillSerializer(serializers.ModelSerializer):
    mentor_details = UserProfileSerializer(source="mentor", read_only=True)

    class Meta:
        model = Skill
        fields = [
            "id",
            "mentor",
            "mentor_details",
            "title",
            "category",
            "level",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "mentor", "created_at"]
