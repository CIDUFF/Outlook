"""
Monkey patch para capturar exceção real do Google OAuth callback
"""
import logging
from allauth.socialaccount.providers.oauth2 import views as oauth2_views
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.providers.base.constants import AuthError

logger = logging.getLogger('allauth')

# Guardar o método original
_original_get_login_data = oauth2_views.OAuth2CallbackView.get_login_data

def patched_get_login_data(self, request, app):
    """
    Versão patched que loga a exceção real
    """
    try:
        return _original_get_login_data(self, request, app)
    except Exception as e:
        logger.error(f"GOOGLE OAUTH ERROR in get_login_data: {type(e).__name__}: {str(e)}", exc_info=True)
        raise

# Aplicar o patch
oauth2_views.OAuth2CallbackView.get_login_data = patched_get_login_data

# Também fazer patch na função complete_login
_original_complete_social_login = oauth2_views.complete_social_login if hasattr(oauth2_views, 'complete_social_login') else None

if _original_complete_social_login:
    def patched_complete_social_login(request, login):
        try:
            return _original_complete_social_login(request, login)
        except Exception as e:
            logger.error(f"GOOGLE OAUTH ERROR in complete_social_login: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
    
    oauth2_views.complete_social_login = patched_complete_social_login

logger.info("Google OAuth error logging patch applied!")
