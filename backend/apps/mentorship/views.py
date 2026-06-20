from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.skills.models import Skill

from .models import AIMatchResult, LearningPath, MentorshipRequest
from .serializers import (
    AIMatchResultSerializer,
    LearningPathSerializer,
    MentorshipRequestSerializer,
)
from .tasks import generate_ai_mentor_matches, generate_learning_path


class MentorshipRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = MentorshipRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return MentorshipRequest.objects.filter(
            learner=user
        ) | MentorshipRequest.objects.filter(mentor=user)

    def perform_create(self, serializer):
        if self.request.user.role != "learner":
            raise PermissionDenied(
                "Only active learner profiles can submit mentorship placement requests."
            )
        serializer.save(learner=self.request.user)


class MentorshipRequestActionView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            req = MentorshipRequest.objects.get(id=pk, mentor=request.user)
        except MentorshipRequest.DoesNotExist:
            return Response(
                {"error": "Inquiry record not found or unauthorized access."},
                status=status.HTTP_404_NOT_FOUND,
            )

        action = request.data.get("action")
        if action not in ["accepted", "rejected"]:
            return Response(
                {"error": "Invalid action. Must be 'accepted' or 'rejected'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        req.status = action
        req.save()

        return Response(
            MentorshipRequestSerializer(req).data, status=status.HTTP_200_OK
        )


class TriggerLearningPathView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        goal = request.data.get("goal")
        if not goal:
            return Response(
                {"error": "Goal parameter field is missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pathway = LearningPath.objects.create(
            user=request.user,
            goal=goal,
            title="Processing via AI...",
            content={},
        )

        try:
            generate_learning_path(pathway.id, goal)
        except Exception:
            pathway.delete()
            return Response(
                {"error": "Failed to generate learning path. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        pathway.refresh_from_db()
        return Response(
            LearningPathSerializer(pathway).data,
            status=status.HTTP_201_CREATED,
        )


class AIMentorMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        goal = request.data.get("goal")
        if not goal:
            return Response(
                {"error": "Goal parameter field is missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        time_threshold = timezone.now() - timedelta(hours=24)
        cached_result = AIMatchResult.objects.filter(
            goal__iexact=goal, created_at__gte=time_threshold
        ).first()

        if cached_result:
            return Response(
                {"source": "cache", "results": cached_result.results},
                status=status.HTTP_200_OK,
            )

        skills_pool = Skill.objects.all().values(
            "mentor_id", "title", "category", "description"
        )
        mentors_context_list = list(skills_pool)

        match_entry = AIMatchResult.objects.create(
            learner=request.user, goal=goal, results={}
        )

        try:
            generate_ai_mentor_matches(match_entry.id, mentors_context_list, goal)
        except Exception:
            match_entry.delete()
            return Response(
                {"error": "Failed to match mentors. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        match_entry.refresh_from_db()
        return Response(
            {"source": "live", "results": match_entry.results},
            status=status.HTTP_200_OK,
        )


class LearningPathDetailView(generics.RetrieveAPIView):
    queryset = LearningPath.objects.all()
    serializer_class = LearningPathSerializer
    permission_classes = [IsAuthenticated]


class AIMatchResultDetailView(generics.RetrieveAPIView):
    queryset = AIMatchResult.objects.all()
    serializer_class = AIMatchResultSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(
            {"source": "cache", "results": instance.results},
            status=status.HTTP_200_OK,
        )
