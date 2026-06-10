from rest_framework import serializers

from .models import MentorProfile, UserProfile


class MentorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorProfile
        fields = ["experience_yrs", "availability", "linkedin_url", "ai_summary"]
        read_only_fields = ["ai_summary"]


class UserProfileSerializer(serializers.ModelSerializer):
    mentor_profile = MentorProfileSerializer(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "display_name",
            "bio",
            "avatar_url",
            "role",
            "created_at",
            "mentor_profile",
        ]
        read_only_fields = ["id", "created_at"]

    def update(self, instance, validated_data):
        mentor_profile_data = validated_data.pop("mentor_profile", None)

        instance.display_name = validated_data.get(
            "display_name", instance.display_name
        )
        instance.bio = validated_data.get("bio", instance.bio)
        instance.avatar_url = validated_data.get("avatar_url", instance.avatar_url)
        instance.role = validated_data.get("role", instance.role)
        instance.save()

        if instance.role == "mentor" and mentor_profile_data:
            MentorProfile.objects.update_or_create(
                id=instance, defaults=mentor_profile_data
            )
        return instance
