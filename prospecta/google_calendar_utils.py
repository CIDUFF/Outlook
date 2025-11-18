"""
Utilitários para integração com Google Calendar API
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

# Lazy import do Google API (só carrega se necessário)
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    logger.warning(
        "Google API client not installed. Google Calendar integration disabled.")


class GoogleCalendarManager:
    """Gerenciador de eventos do Google Calendar"""

    def __init__(self, access_token: str, refresh_token: str, token_expiry: datetime):
        """
        Inicializa o gerenciador com credenciais OAuth

        Args:
            access_token: Token de acesso OAuth
            refresh_token: Token de refresh para renovação
            token_expiry: Data/hora de expiração do token
        """
        if not GOOGLE_API_AVAILABLE:
            raise ImportError("Google API client library not installed")

        # Verificar se token expirou e precisa de refresh
        from django.conf import settings
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', ''),
            client_secret=getattr(settings, 'GOOGLE_OAUTH2_CLIENT_SECRET', ''),
        )

        # Se o token expirou, tentar refresh
        if self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())

        self.service = build('calendar', 'v3', credentials=self.credentials)

    def create_event(
        self,
        calendar_id: str,
        summary: str,
        description: str,
        start_datetime: datetime,
        end_datetime: datetime,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Cria um evento no Google Calendar

        Args:
            calendar_id: ID do calendário (geralmente 'primary')
            summary: Título do evento
            description: Descrição do evento
            start_datetime: Data/hora de início
            end_datetime: Data/hora de término
            location: Local do evento (opcional)
            attendees: Lista de emails dos participantes (opcional)

        Returns:
            Dict com dados do evento criado ou None se falhar
        """
        try:
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
            }

            if location:
                event['location'] = location

            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            result = self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates='all'  # Envia convites por email
            ).execute()

            logger.info(f"Event created: {result.get('id')}")
            return result

        except HttpError as error:
            logger.error(f"Error creating event: {error}")
            return None

    def update_event(
        self,
        calendar_id: str,
        event_id: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Atualiza um evento existente no Google Calendar

        Args:
            calendar_id: ID do calendário
            event_id: ID do evento a ser atualizado
            summary: Novo título (opcional)
            description: Nova descrição (opcional)
            start_datetime: Nova data/hora de início (opcional)
            end_datetime: Nova data/hora de término (opcional)
            location: Novo local (opcional)
            attendees: Nova lista de emails (opcional)

        Returns:
            Dict com dados do evento atualizado ou None se falhar
        """
        try:
            # Buscar evento atual
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # Atualizar campos fornecidos
            if summary:
                event['summary'] = summary
            if description:
                event['description'] = description
            if start_datetime:
                event['start'] = {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                }
            if end_datetime:
                event['end'] = {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                }
            if location is not None:
                event['location'] = location
            if attendees is not None:
                event['attendees'] = [{'email': email} for email in attendees]

            result = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()

            logger.info(f"Event updated: {event_id}")
            return result

        except HttpError as error:
            logger.error(f"Error updating event: {error}")
            return None

    def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """
        Deleta um evento do Google Calendar

        Args:
            calendar_id: ID do calendário
            event_id: ID do evento a ser deletado

        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()

            logger.info(f"Event deleted: {event_id}")
            return True

        except HttpError as error:
            logger.error(f"Error deleting event: {error}")
            return False

    def list_events(
        self,
        calendar_id: str,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Lista eventos do calendário

        Args:
            calendar_id: ID do calendário
            time_min: Data/hora mínima (opcional)
            time_max: Data/hora máxima (opcional)
            max_results: Número máximo de resultados

        Returns:
            Lista de eventos
        """
        try:
            if not time_min:
                time_min = datetime.utcnow()

            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z' if time_max else None,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            return events_result.get('items', [])

        except HttpError as error:
            logger.error(f"Error listing events: {error}")
            return []


def get_or_create_google_integration(user):
    """
    Obtém ou cria integração do Google Calendar para um usuário

    Args:
        user: Instância do User

    Returns:
        Instância do GoogleCalendarIntegration ou None
    """
    from .models import GoogleCalendarIntegration

    try:
        integration = GoogleCalendarIntegration.objects.get(user=user)
        if not integration.access_token:
            logger.warning(f"No access token for user {user.username}")
            return None
        return integration
    except GoogleCalendarIntegration.DoesNotExist:
        logger.info(f"No Google Calendar integration for user {user.username}")
        return None


def sync_meeting_to_google_calendar(meeting) -> bool:
    """
    Sincroniza uma reunião do PROSPECTA com Google Calendar

    Args:
        meeting: Instância do modelo Meeting

    Returns:
        True se sincronizado com sucesso, False caso contrário
    """
    if not GOOGLE_API_AVAILABLE:
        logger.warning("Google API not available")
        return False

    try:
        # Verificar se organizador tem integração Google Calendar
        integration = meeting.organizer.google_calendar
        if not integration or not integration.is_active:
            logger.info(
                f"No active Google Calendar integration for {meeting.organizer}")
            return False

        # Criar gerenciador
        manager = GoogleCalendarManager(
            access_token=integration.access_token,
            refresh_token=integration.refresh_token,
            token_expiry=integration.token_expiry
        )

        # Preparar lista de emails dos participantes
        attendee_emails = [
            user.email for user in meeting.attendees.all() if user.email]

        if meeting.google_event_id:
            # Atualizar evento existente
            result = manager.update_event(
                calendar_id=integration.calendar_id,
                event_id=meeting.google_event_id,
                summary=meeting.title,
                description=meeting.description,
                start_datetime=meeting.start_datetime,
                end_datetime=meeting.end_datetime,
                location=meeting.location,
                attendees=attendee_emails
            )
        else:
            # Criar novo evento
            result = manager.create_event(
                calendar_id=integration.calendar_id,
                summary=meeting.title,
                description=meeting.description,
                start_datetime=meeting.start_datetime,
                end_datetime=meeting.end_datetime,
                location=meeting.location,
                attendees=attendee_emails
            )

        if result:
            meeting.google_event_id = result.get('id')
            meeting.synced_with_google = True
            meeting.save(update_fields=[
                         'google_event_id', 'synced_with_google'])
            return True

        return False

    except Exception as e:
        logger.error(f"Error syncing meeting to Google Calendar: {e}")
        return False


def delete_meeting_from_google_calendar(meeting) -> bool:
    """
    Remove uma reunião do Google Calendar

    Args:
        meeting: Instância do modelo Meeting

    Returns:
        True se removido com sucesso, False caso contrário
    """
    if not GOOGLE_API_AVAILABLE or not meeting.google_event_id:
        return False

    try:
        integration = meeting.organizer.google_calendar
        if not integration or not integration.is_active:
            return False

        manager = GoogleCalendarManager(
            access_token=integration.access_token,
            refresh_token=integration.refresh_token,
            token_expiry=integration.token_expiry
        )

        return manager.delete_event(
            calendar_id=integration.calendar_id,
            event_id=meeting.google_event_id
        )

    except Exception as e:
        logger.error(f"Error deleting meeting from Google Calendar: {e}")
        return False
