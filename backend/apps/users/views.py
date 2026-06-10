from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from supabase import Client, create_client

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
