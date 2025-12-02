"""
Serviço de notificações por email e in-app para o sistema PROSPECTA.
Suporta django-background-tasks para envio assíncrono de emails.
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

# Tentar importar background_task, se não disponível, usar execução síncrona
try:
    from background_task import background
    ASYNC_ENABLED = True
except ImportError:
    ASYNC_ENABLED = False
    # Decorator dummy quando background_task não está instalado

    def background(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


def get_site_url():
    """Retorna a URL base do site"""
    if hasattr(settings, 'SITE_URL'):
        return settings.SITE_URL
    if hasattr(settings, 'ALLOWED_HOSTS') and settings.ALLOWED_HOSTS:
        host = settings.ALLOWED_HOSTS[0]
        if host == '*':
            host = 'localhost:8555'
        protocol = 'https' if not settings.DEBUG else 'http'
        return f"{protocol}://{host}"
    return 'http://localhost:8555'


# ============================================================================
# CRIAÇÃO DE NOTIFICAÇÕES IN-APP
# ============================================================================

def create_notification(
    recipient,
    notification_type,
    title,
    message,
    sender=None,
    related_activity=None,
    related_opportunity=None,
    action_url=None,
    priority='normal',
    send_email=True
):
    """
    Cria uma notificação in-app e opcionalmente envia email.

    Args:
        recipient: User que receberá a notificação
        notification_type: Tipo da notificação (activity_assigned, etc.)
        title: Título da notificação
        message: Mensagem detalhada
        sender: User que está enviando (opcional)
        related_activity: Activity relacionada (opcional)
        related_opportunity: Opportunity relacionada (opcional)
        action_url: URL para ação (opcional)
        priority: Prioridade (low, normal, high, urgent)
        send_email: Se deve enviar email também

    Returns:
        Notification: Instância criada
    """
    from .models import Notification

    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        title=title,
        message=message,
        related_activity=related_activity,
        related_opportunity=related_opportunity,
        action_url=action_url,
        priority=priority,
    )

    # Enviar email se solicitado e se o destinatário tem email
    if send_email and recipient.email:
        if ASYNC_ENABLED:
            send_notification_email_async(
                str(notification.id),
                recipient.id,
                title,
                message,
                action_url or ''
            )
        else:
            send_notification_email_sync(
                notification, recipient, title, message, action_url)

    return notification


def send_notification_email_sync(notification, recipient, title, message, action_url):
    """Envia email de notificação de forma síncrona"""
    try:
        context = {
            'recipient_name': recipient.get_full_name() or recipient.username,
            'title': title,
            'message': message,
            'action_url': f"{get_site_url()}{action_url}" if action_url else None,
            'site_url': get_site_url(),
        }

        html_message = render_to_string(
            'prospecta/emails/notification.html', context)
        plain_message = render_to_string(
            'prospecta/emails/notification.txt', context)

        # Usar EmailMultiAlternatives para garantir que HTML seja enviado corretamente
        msg = EmailMultiAlternatives(
            subject=f"[PROSPECTA] {title}",
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient.email],
        )
        msg.attach_alternative(html_message, 'text/html')
        msg.send(fail_silently=True)

        # Marcar email como enviado
        notification.email_sent = True
        notification.email_sent_at = timezone.now()
        notification.save(update_fields=['email_sent', 'email_sent_at'])

    except Exception as e:
        logger.error(f"Erro ao enviar email de notificação: {e}")


@background(schedule=0)
def send_notification_email_async(notification_id, recipient_id, title, message, action_url):
    """Envia email de notificação de forma assíncrona via django-background-tasks"""
    from django.contrib.auth.models import User
    from .models import Notification

    try:
        notification = Notification.objects.get(id=notification_id)
        recipient = User.objects.get(id=recipient_id)

        send_notification_email_sync(
            notification, recipient, title, message, action_url)

    except Exception as e:
        logger.error(f"Erro ao enviar email assíncrono: {e}")


# ============================================================================
# NOTIFICAÇÕES ESPECÍFICAS DE ATIVIDADES
# ============================================================================

def notify_activity_assigned(activity, assigned_by):
    """
    Notifica o usuário quando uma atividade é atribuída a ele.

    Args:
        activity: Activity que foi atribuída
        assigned_by: User que atribuiu a atividade
    """
    if not activity.assigned_to or activity.assigned_to == assigned_by:
        return None

    opportunity = activity.stage.opportunity
    # Apontar para a página de submissão da atividade
    action_url = reverse('prospecta:activity_submit_completion',
                         kwargs={'pk': activity.pk})

    title = f"Nova atividade atribuída: {activity.title}"
    message = (
        f"{assigned_by.get_full_name()} atribuiu a atividade '{activity.title}' para você.\n\n"
        f"Oportunidade: {opportunity.title}\n"
        f"Etapa: {activity.stage.name}\n"
        f"Tipo: {activity.get_activity_type_display()}\n"
    )
    if activity.expected_date:
        # Garantir que expected_date é um objeto date
        if hasattr(activity.expected_date, 'strftime'):
            message += f"Data esperada: {activity.expected_date.strftime('%d/%m/%Y')}\n"
        else:
            message += f"Data esperada: {activity.expected_date}\n"
    if activity.description:
        message += f"\nDescrição: {activity.description}"

    return create_notification(
        recipient=activity.assigned_to,
        notification_type='activity_assigned',
        title=title,
        message=message,
        sender=assigned_by,
        related_activity=activity,
        related_opportunity=opportunity,
        action_url=action_url,
        priority='high',
    )


def notify_activity_reassigned(activity, old_assignee, new_assignee, reassigned_by):
    """
    Notifica quando uma atividade é reatribuída de um usuário para outro.

    Args:
        activity: Activity reatribuída
        old_assignee: User anterior
        new_assignee: Novo User
        reassigned_by: User que fez a reatribuição
    """
    opportunity = activity.stage.opportunity
    # Apontar para a página de submissão da atividade
    action_url = reverse('prospecta:activity_submit_completion',
                         kwargs={'pk': activity.pk})

    notifications = []

    # Notificar o novo responsável
    if new_assignee and new_assignee != reassigned_by:
        title = f"Atividade reatribuída para você: {activity.title}"
        message = (
            f"{reassigned_by.get_full_name()} reatribuiu a atividade '{activity.title}' para você.\n\n"
            f"Responsável anterior: {old_assignee.get_full_name() if old_assignee else 'Nenhum'}\n"
            f"Oportunidade: {opportunity.title}\n"
            f"Etapa: {activity.stage.name}"
        )

        notifications.append(create_notification(
            recipient=new_assignee,
            notification_type='activity_reassigned',
            title=title,
            message=message,
            sender=reassigned_by,
            related_activity=activity,
            related_opportunity=opportunity,
            action_url=action_url,
            priority='high',
        ))

    # Notificar o responsável anterior
    if old_assignee and old_assignee != reassigned_by and old_assignee != new_assignee:
        title = f"Atividade reatribuída: {activity.title}"
        message = (
            f"A atividade '{activity.title}' foi reatribuída para "
            f"{new_assignee.get_full_name() if new_assignee else 'ninguém'}.\n\n"
            f"Reatribuído por: {reassigned_by.get_full_name()}"
        )

        notifications.append(create_notification(
            recipient=old_assignee,
            notification_type='activity_reassigned',
            title=title,
            message=message,
            sender=reassigned_by,
            related_activity=activity,
            related_opportunity=opportunity,
            action_url=action_url,
            priority='normal',
        ))

    return notifications


def notify_activity_submitted_for_verification(activity, submitted_by):
    """
    Notifica o verificador quando uma atividade é submetida para verificação.

    Args:
        activity: Activity submetida
        submitted_by: User que submeteu
    """
    if not activity.verifier:
        return None

    opportunity = activity.stage.opportunity
    action_url = reverse('prospecta:activity_verify',
                         kwargs={'pk': activity.pk})

    title = f"Atividade aguardando verificação: {activity.title}"
    message = (
        f"{submitted_by.get_full_name()} submeteu a atividade '{activity.title}' para sua verificação.\n\n"
        f"Oportunidade: {opportunity.title}\n"
        f"Etapa: {activity.stage.name}\n\n"
        f"Notas de conclusão:\n{activity.completion_notes or 'Nenhuma nota adicionada.'}"
    )

    return create_notification(
        recipient=activity.verifier,
        notification_type='activity_submitted',
        title=title,
        message=message,
        sender=submitted_by,
        related_activity=activity,
        related_opportunity=opportunity,
        action_url=action_url,
        priority='high',
    )


def notify_activity_approved(activity, approved_by):
    """
    Notifica o responsável quando uma atividade é aprovada.

    Args:
        activity: Activity aprovada
        approved_by: User que aprovou
    """
    # Notificar o responsável anterior (quem executou a atividade)
    if not activity.previous_assigned_to:
        return None

    opportunity = activity.stage.opportunity
    # Apontar para a lista de atividades
    action_url = reverse('prospecta:activities_list')

    title = f"Atividade aprovada: {activity.title}"

    # Formatar data de aprovação de forma segura
    approval_date_str = 'N/A'
    if activity.approval_date:
        if hasattr(activity.approval_date, 'strftime'):
            approval_date_str = activity.approval_date.strftime(
                '%d/%m/%Y %H:%M')
        else:
            approval_date_str = str(activity.approval_date)

    message = (
        f"{approved_by.get_full_name()} aprovou a atividade '{activity.title}'.\n\n"
        f"Oportunidade: {opportunity.title}\n"
        f"Etapa: {activity.stage.name}\n"
        f"Data de aprovação: {approval_date_str}"
    )

    return create_notification(
        recipient=activity.previous_assigned_to,
        notification_type='activity_approved',
        title=title,
        message=message,
        sender=approved_by,
        related_activity=activity,
        related_opportunity=opportunity,
        action_url=action_url,
        priority='normal',
    )


def notify_activity_rejected(activity, rejected_by, rejection_reason):
    """
    Notifica o responsável quando uma atividade é reprovada.

    Args:
        activity: Activity reprovada
        rejected_by: User que reprovou
        rejection_reason: Motivo da reprovação
    """
    # Notificar o responsável anterior (quem executou a atividade)
    if not activity.previous_assigned_to:
        return None

    opportunity = activity.stage.opportunity
    # Apontar para a página de submissão para corrigir
    action_url = reverse('prospecta:activity_submit_completion',
                         kwargs={'pk': activity.pk})

    title = f"Atividade reprovada: {activity.title}"
    message = (
        f"{rejected_by.get_full_name()} reprovou a atividade '{activity.title}'.\n\n"
        f"Oportunidade: {opportunity.title}\n"
        f"Etapa: {activity.stage.name}\n\n"
        f"Motivo da reprovação:\n{rejection_reason}\n\n"
        f"A atividade foi reatribuída para você para correções."
    )

    return create_notification(
        recipient=activity.previous_assigned_to,
        notification_type='activity_rejected',
        title=title,
        message=message,
        sender=rejected_by,
        related_activity=activity,
        related_opportunity=opportunity,
        action_url=action_url,
        priority='urgent',
    )


def notify_activity_comment(comment):
    """
    Notifica quando um comentário é adicionado a uma atividade.

    Args:
        comment: ActivityComment criado
    """
    activity = comment.activity
    opportunity = activity.stage.opportunity
    # Se a atividade está aguardando verificação, apontar para verificação
    if activity.status == 'aguardando_verificacao':
        action_url = reverse('prospecta:activity_verify',
                             kwargs={'pk': activity.pk})
    else:
        action_url = reverse('prospecta:activity_submit_completion',
                             kwargs={'pk': activity.pk})

    # Determinar quem deve ser notificado
    recipients = set()

    if activity.assigned_to and activity.assigned_to != comment.author:
        recipients.add(activity.assigned_to)

    if activity.verifier and activity.verifier != comment.author:
        recipients.add(activity.verifier)

    if activity.delegated_by and activity.delegated_by != comment.author:
        recipients.add(activity.delegated_by)

    notifications = []
    for recipient in recipients:
        title = f"Novo comentário em: {activity.title}"
        message = (
            f"{comment.author.get_full_name()} comentou na atividade '{activity.title}':\n\n"
            f'"{comment.content[:200]}{"..." if len(comment.content) > 200 else ""}"'
        )

        notifications.append(create_notification(
            recipient=recipient,
            notification_type='activity_comment',
            title=title,
            message=message,
            sender=comment.author,
            related_activity=activity,
            related_opportunity=opportunity,
            action_url=action_url,
            priority='normal',
        ))

    return notifications


# ============================================================================
# NOTIFICAÇÕES DE OPORTUNIDADES (mantendo compatibilidade)
# ============================================================================

def notify_opportunity_participants(opportunity, changed_by, change_type, change_details):
    """
    Notifica todos os participantes de uma oportunidade sobre mudanças.

    Args:
        opportunity: Instância de Opportunity
        changed_by: User que fez a mudança
        change_type: Tipo de mudança (status, etapa, atividade, etc)
        change_details: Detalhes da mudança
    """
    # Obter participantes que desejam ser notificados
    participants = opportunity.participants.filter(notify_on_update=True)

    if not participants.exists():
        return []

    action_url = reverse('prospecta:opportunity_detail',
                         kwargs={'pk': opportunity.pk})
    title = f"Atualização em: {opportunity.title}"

    notifications = []
    for participant in participants:
        if participant.user != changed_by:
            notifications.append(create_notification(
                recipient=participant.user,
                notification_type='opportunity_update',
                title=title,
                message=f"{changed_by.get_full_name()} fez uma alteração:\n\n{change_details}",
                sender=changed_by,
                related_opportunity=opportunity,
                action_url=action_url,
                priority='normal',
            ))

    return notifications


def notify_status_change(opportunity, old_status, new_status, changed_by):
    """Notifica sobre mudança de status"""
    change_details = f"Status alterado de '{old_status}' para '{new_status}'"
    return notify_opportunity_participants(
        opportunity,
        changed_by,
        'mudança_de_status',
        change_details
    )


def notify_stage_update(opportunity, stage, changed_by):
    """Notifica sobre mudança em etapa"""
    change_details = f"Etapa '{stage.name}' foi atualizada"
    return notify_opportunity_participants(
        opportunity,
        changed_by,
        'atualização_de_etapa',
        change_details
    )


def notify_activity_update(opportunity, activity, changed_by):
    """Notifica sobre mudança em atividade"""
    change_details = f"Atividade '{activity.title}' foi atualizada"
    return notify_opportunity_participants(
        opportunity,
        changed_by,
        'atualização_de_atividade',
        change_details
    )


# ============================================================================
# UTILITÁRIOS
# ============================================================================

def get_unread_notifications_count(user):
    """Retorna a contagem de notificações não lidas do usuário"""
    from .models import Notification
    return Notification.objects.filter(recipient=user, is_read=False).count()


def get_recent_notifications(user, limit=10):
    """Retorna as notificações mais recentes do usuário"""
    from .models import Notification
    return Notification.objects.filter(recipient=user).order_by('-created_at')[:limit]


def mark_all_as_read(user):
    """Marca todas as notificações do usuário como lidas"""
    from .models import Notification
    now = timezone.now()
    return Notification.objects.filter(
        recipient=user,
        is_read=False
    ).update(is_read=True, read_at=now)
