# authentication.py

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from supabase import create_client

from apps.users.models import UserProfile

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY,
)


class SupabaseJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        try:
            token = auth_header.split(" ")[1]

            user_response = supabase.auth.get_user(token)

            if not user_response.user:
                raise AuthenticationFailed("Invalid token")

            user = UserProfile.objects.get(id=user_response.user.id)

            return (user, token)

        except Exception:
            raise AuthenticationFailed("Invalid token")
