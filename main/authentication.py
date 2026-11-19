from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    """Authenticate Django's existing users by email, without revealing account existence."""
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = (kwargs.get('email') or username or '').strip().lower()
        if not email or password is None:
            return None
        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            User().set_password(password)  # burn comparable password-hashing work
            return None
        return user if user.check_password(password) and self.user_can_authenticate(user) else None
