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
from .tasks import generate_ai_mentor_matches_task, generate_learning_path_task


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

        action = request.data.get("action")  # "accepted" or "rejected"
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
            content={"status": "queued"},
        )

        generate_learning_path_task.delay(pathway.id, goal)

        return Response(
            {
                "message": "AI roadmap processing has been offloaded to queue.",
                "pathway_id": pathway.id,
            },
            status=status.HTTP_202_ACCEPTED,
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

        new_match_entry = AIMatchResult.objects.create(
            learner=request.user, goal=goal, results={"status": "processing"}
        )

        generate_ai_mentor_matches_task.delay(
            new_match_entry.id, goal, mentors_context_list
        )

        return Response(
            {
                "source": "queued",
                "message": "Orchestrating background matching evaluation grid.",
                "match_id": new_match_entry.id,
            },
            status=status.HTTP_202_ACCEPTED,
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

        if (
            isinstance(instance.results, dict)
            and instance.results.get("status") == "processing"
        ):
            return Response(
                {"source": "queued", "results": []}, status=status.HTTP_200_OK
            )

        return Response(
            {"source": "cache", "results": instance.results}, status=status.HTTP_200_OK
        )
