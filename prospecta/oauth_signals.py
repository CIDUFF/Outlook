"""
Signals para capturar OAuth do Google Calendar
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.contrib.auth import get_user_model
import logging

from .models import GoogleCalendarIntegration

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=SocialAccount)
def save_google_tokens(sender, instance, created, **kwargs):
    """
    Salva tokens do Google Calendar quando usuário se conecta via OAuth
    """
    if instance.provider == 'google':
        try:
            # Obter ou criar integração
            integration, created = GoogleCalendarIntegration.objects.get_or_create(
                user=instance.user,
                defaults={
                    'calendar_id': 'primary',
                    'is_active': True,
                }
            )

            # Obter tokens
            try:
                social_token = SocialToken.objects.get(account=instance)
                integration.access_token = social_token.token
                integration.refresh_token = social_token.token_secret
                integration.token_expiry = social_token.expires_at
                integration.is_active = True
                integration.save()

                logger.info(
                    f"Google Calendar tokens saved for user {instance.user.username}")

            except SocialToken.DoesNotExist:
                logger.warning(
                    f"No SocialToken found for Google account {instance}")
                integration.is_active = False
                integration.save()

        except Exception as e:
            logger.error(f"Error saving Google Calendar tokens: {e}")
