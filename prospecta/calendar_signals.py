"""
Signals para sincronização automática de calendário e documentos
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import logging

from .models import Meeting, OpportunityDocument, ActivityAttachment, OpportunityHistory, ActivityHistory
from .middleware import get_current_user

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Meeting)
def sync_meeting_to_calendar(sender, instance, created, **kwargs):
    """Sincroniza reunião com Google Calendar automaticamente"""
    # Importar aqui para evitar circular import
    from .google_calendar_utils import sync_meeting_to_google_calendar

    if instance.status != 'cancelada':
        sync_meeting_to_google_calendar(instance)


@receiver(pre_delete, sender=Meeting)
def remove_meeting_from_calendar(sender, instance, **kwargs):
    """Remove reunião do Google Calendar antes de deletar"""
    from .google_calendar_utils import delete_meeting_from_google_calendar

    if instance.google_event_id:
        delete_meeting_from_google_calendar(instance)


@receiver(post_save, sender=OpportunityDocument)
def log_document_upload(sender, instance, created, **kwargs):
    """Registra upload de documento no histórico da oportunidade"""
    if created:
        OpportunityHistory.objects.create(
            opportunity=instance.opportunity,
            changed_by=instance.uploaded_by or get_current_user(),
            change_type='DOCUMENTO_ADICIONADO',
            change_details=f'Documento "{instance.title}" ({instance.get_document_type_display()}) adicionado'
        )


@receiver(post_save, sender=ActivityAttachment)
def log_attachment_upload(sender, instance, created, **kwargs):
    """Registra upload de anexo no histórico da atividade"""
    if created:
        ActivityHistory.objects.create(
            activity=instance.activity,
            changed_by=instance.uploaded_by or get_current_user(),
            change_type='ANEXO_ADICIONADO',
            change_details='Anexo adicionado à atividade'
        )
