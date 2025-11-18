"""
Context processors for prospecta app
Provides common context variables to all templates
"""
from .utils import get_user_context


def auth_context(request):
    """
    Add authentication context to all templates
    """
    if request.user.is_authenticated:
        context = get_user_context(request.user)
        context['user'] = request.user
        return context
    return {}
