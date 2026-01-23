from django.utils import timezone
from ..models import Mute


def is_user_muted(user):
    """Check if user is currently muted."""
    return Mute.objects.filter(user=user, expires_at__gt=timezone.now()).exists()


def get_active_mute(user):
    """Get active mute for user if exists."""
    return Mute.objects.filter(user=user, expires_at__gt=timezone.now()).first()

