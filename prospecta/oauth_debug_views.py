"""
Custom OAuth2 callback view com logging completo de erros
"""
import logging
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger('allauth')


class DebugGoogleOAuth2CallbackView(OAuth2CallbackView):
    adapter_class = GoogleOAuth2Adapter
    
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"=== GOOGLE OAUTH CALLBACK DEBUG ===")
        logger.info(f"GET params: {dict(request.GET.items())}")
        logger.info(f"POST params: {dict(request.POST.items())}")
        logger.info(f"Session: {dict(request.session.items())}")
        
        try:
            response = super().dispatch(request, *args, **kwargs)
            logger.info(f"Callback succeeded, redirecting to: {response.get('Location', 'N/A')}")
            return response
        except Exception as e:
            logger.error(f"Callback error: {type(e).__name__}: {str(e)}", exc_info=True)
            raise


debug_google_oauth2_callback = csrf_exempt(DebugGoogleOAuth2CallbackView.as_view())
