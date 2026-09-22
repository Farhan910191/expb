from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class CaseInsensitiveEmailOrUsernameBackend(ModelBackend):
    """
    Authenticate using either case-insensitive username or email,
    and automatically strip leading/trailing spaces (crucial for mobile devices).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if not username or not password:
            return None

        clean_username = str(username).strip()
        try:
            user = UserModel.objects.filter(
                Q(username__iexact=clean_username) | Q(email__iexact=clean_username)
            ).first()
        except Exception:
            return None

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
