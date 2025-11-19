"""
Signals para sincronização automática de documentos e anexos
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

from .models import OpportunityDocument, ActivityAttachment, OpportunityHistory, ActivityHistory
from .middleware import get_current_user

logger = logging.getLogger(__name__)


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

