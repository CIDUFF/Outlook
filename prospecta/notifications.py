"""
Serviço de notificações por email para mudanças em oportunidades
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse


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
        return

    # Preparar contexto do email
    context = {
        'opportunity': opportunity,
        'changed_by': changed_by,
        'change_type': change_type,
        'change_details': change_details,
        'opportunity_url': f"{settings.ALLOWED_HOSTS[0]}/oportunidades/{opportunity.pk}/",
    }

    # Listar destinatários
    recipients = [p.user.email for p in participants if p.user.email]

    if not recipients:
        return

    # Renderizar template do email
    subject = f"[Oportunidade {opportunity.title}] - Alteração: {change_type}"

    html_message = render_to_string(
        'prospecta/emails/opportunity_notification.html', context)
    plain_message = render_to_string(
        'prospecta/emails/opportunity_notification.txt', context)

    # Enviar email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erro ao enviar notificação de oportunidade: {e}")


def notify_status_change(opportunity, old_status, new_status, changed_by):
    """Notifica sobre mudança de status"""
    change_details = f"Status alterado de '{old_status}' para '{new_status}'"
    notify_opportunity_participants(
        opportunity,
        changed_by,
        'mudança_de_status',
        change_details
    )


def notify_stage_update(opportunity, stage, changed_by):
    """Notifica sobre mudança em etapa"""
    change_details = f"Etapa '{stage.name}' foi atualizada"
    notify_opportunity_participants(
        opportunity,
        changed_by,
        'atualização_de_etapa',
        change_details
    )


def notify_activity_update(opportunity, activity, changed_by):
    """Notifica sobre mudança em atividade"""
    change_details = f"Atividade '{activity.title}' foi atualizada"
    notify_opportunity_participants(
        opportunity,
        changed_by,
        'atualização_de_atividade',
        change_details
    )
