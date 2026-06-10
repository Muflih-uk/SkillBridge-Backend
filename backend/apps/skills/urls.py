from django.urls import path

from .views import SkillListCreateView, SkillRetrieveUpdateDestroyView

urlpatterns = [
    path("", SkillListCreateView.as_view(), name="skill-list-create"),
    path("<uuid:pk>/", SkillRetrieveUpdateDestroyView.as_view(), name="skill-detail"),
]
