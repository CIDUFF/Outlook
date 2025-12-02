"""
Context processors for prospecta app
Provides common context variables to all templates
"""
from .utils import get_user_context
from .notifications import get_unread_notifications_count


def auth_context(request):
    """
    Add authentication context to all templates
    """
    if request.user.is_authenticated:
        context = get_user_context(request.user)
        context['user'] = request.user
        # Adicionar contagem de notificações não lidas
        context['unread_notifications_count'] = get_unread_notifications_count(
            request.user)
        return context
    return {}
