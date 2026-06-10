from django.db.models import Q
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Skill
from .serializers import SkillSerializer


class SkillListCreateView(generics.ListCreateAPIView):
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Skill.objects.all().select_related("mentor")

        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(category__icontains=search_query)
            )

        category = self.request.query_params.get("category", None)
        level = self.request.query_params.get("level", None)

        if category:
            queryset = queryset.filter(category__iexact=category)
        if level:
            queryset = queryset.filter(level__iexact=level)

        return queryset

    def perform_create(self, serializer):
        if self.request.user.role != "mentor":
            raise PermissionDenied("Only registered mentors can create skill listings.")
        serializer.save(mentor=self.request.user)


class SkillRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if serializer.instance.mentor != self.request.user:
            raise PermissionDenied("You do not own this skill listing.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.mentor != self.request.user:
            raise PermissionDenied("You do not own this skill listing.")
        instance.delete()
