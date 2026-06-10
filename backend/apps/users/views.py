import uuid

from django.conf import settings
from rest_framework import generics, parsers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, PermissionDenied
from supabase import Client, create_client

from apps.mentorship.tasks import generate_mentor_summary_task

from .models import UserProfile
from .serializers import UserProfileSerializer

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        role = request.data.get("role", "learner")
        display_name = request.data.get("display_name", email.split("@")[0])

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            auth_response = supabase.auth.sign_up(
                {"email": email, "password": password}
            )

            user = auth_response.user

            if user:
                UserProfile.objects.get_or_create(
                    id=user.id,
                    defaults={
                        "role": role,
                        "display_name": display_name,
                    },
                )

            return Response(
                {"message": "User registered successfully!", "user_id": user.id},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            auth_response = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            return Response(
                {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "user": {
                        "id": auth_response.user.id,
                        "email": auth_response.user.email,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Invalid credentials or user does not exist."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class CurrentUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        file_obj = request.FILES.get("avatar")
        if not file_obj:
            return Response(
                {"error": "No file detected under the key 'avatar'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            file_extension = file_obj.name.split(".")[-1]
            unique_filename = f"user_{request.user.id}/{uuid.uuid4()}.{file_extension}"

            file_bytes = file_obj.read()
            supabase.storage.from_("avatar").upload(
                path=unique_filename,
                file=file_bytes,
                file_options={"content-type": file_obj.content_type},
            )

            public_url_res = supabase.storage.from_("avatar").get_public_url(
                unique_filename
            )

            user_profile = request.user
            user_profile.avatar_url = public_url_res
            user_profile.save()

            return Response(
                {
                    "message": "Avatar uploaded successfully!",
                    "avatar_url": user_profile.avatar_url,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Storage upload failure: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TriggerMentorSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != "mentor":
            raise PermissionDenied(
                "Only registered mentors can compute professional summaries."
            )

        generate_mentor_summary_task.delay(str(request.user.id))

        return Response(
            {
                "message": "AI profile optimization task successfully offloaded to queue.",
                "status": "processing",
            },
            status=status.HTTP_202_ACCEPTED,
        )
