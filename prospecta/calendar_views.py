"""
Views para gerenciamento de calendário, reuniões e documentos
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime

from .models import (
    Opportunity, Activity, Meeting, OpportunityDocument,
    ActivityAttachment, User
)
from .views import get_user_context, role_required
# ============================================================================
# DOCUMENTOS
# ============================================================================


@login_required(login_url='account_login')
def opportunity_documents(request, pk):
    """Lista documentos de uma oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    context = get_user_context(request.user)

    # Verificar permissão
    profile = request.user.profile
    if not profile.is_admin() and opportunity.responsible_user != request.user and opportunity.created_by != request.user:
        messages.error(
            request, 'Você não tem permissão para acessar estes documentos.')
        return redirect('prospecta:opportunities_list')

    documents = opportunity.documents.all()

    context.update({
        'opportunity': opportunity,
        'documents': documents,
    })

    return render(request, 'prospecta/documents/list.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def upload_opportunity_document(request, pk):
    """Upload de documento para oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)

    if request.method == 'POST':
        title = request.POST.get('title')
        document_type = request.POST.get('document_type', 'outro')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'on'
        file = request.FILES.get('file')

        if not title or not file:
            messages.error(request, 'Título e arquivo são obrigatórios.')
            return redirect('prospecta:opportunity_documents', pk=pk)

        OpportunityDocument.objects.create(
            opportunity=opportunity,
            title=title,
            document_type=document_type,
            file=file,
            description=description,
            uploaded_by=request.user,
            is_public=is_public
        )

        messages.success(request, f'Documento "{title}" enviado com sucesso!')
        return redirect('prospecta:opportunity_documents', pk=pk)

    return redirect('prospecta:opportunity_documents', pk=pk)


@login_required(login_url='account_login')
def delete_opportunity_document(request, pk):
    """Deletar documento"""
    document = get_object_or_404(OpportunityDocument, pk=pk)
    opportunity_pk = document.opportunity.pk

    # Verificar permissão
    profile = request.user.profile
    if not profile.is_admin() and document.uploaded_by != request.user:
        messages.error(
            request, 'Você não tem permissão para deletar este documento.')
        return redirect('prospecta:opportunity_documents', pk=opportunity_pk)

    document_title = document.title
    document.delete()
    messages.success(
        request, f'Documento "{document_title}" deletado com sucesso!')

    return redirect('prospecta:opportunity_documents', pk=opportunity_pk)


@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def upload_activity_attachment(request, pk):
    """Upload de anexo para atividade"""
    activity = get_object_or_404(Activity, pk=pk)

    if request.method == 'POST':
        file = request.FILES.get('file')
        description = request.POST.get('description', '')

        if not file:
            messages.error(request, 'Arquivo é obrigatório.')
            return redirect('prospecta:activity_detail', pk=pk)

        ActivityAttachment.objects.create(
            activity=activity,
            file=file,
            description=description,
            uploaded_by=request.user
        )

        messages.success(request, 'Anexo enviado com sucesso!')
        return redirect('prospecta:activity_detail', pk=pk)

    return redirect('prospecta:activity_detail', pk=pk)


@login_required(login_url='account_login')
def delete_activity_attachment(request, pk):
    """Deletar anexo de atividade"""
    attachment = get_object_or_404(ActivityAttachment, pk=pk)
    activity_pk = attachment.activity.pk

    # Verificar permissão
    profile = request.user.profile
    if not profile.is_admin() and attachment.uploaded_by != request.user:
        messages.error(
            request, 'Você não tem permissão para deletar este anexo.')
        return redirect('prospecta:activity_detail', pk=activity_pk)

    attachment.delete()
    messages.success(request, 'Anexo deletado com sucesso!')

    return redirect('prospecta:activity_detail', pk=activity_pk)


# ============================================================================
# REUNIÕES E CALENDÁRIO
# ============================================================================

@login_required(login_url='account_login')
def opportunity_meetings(request, pk):
    """Lista reuniões de uma oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    context = get_user_context(request.user)

    # Verificar permissão
    profile = request.user.profile
    if not profile.is_admin() and opportunity.responsible_user != request.user and opportunity.created_by != request.user:
        messages.error(
            request, 'Você não tem permissão para acessar estas reuniões.')
        return redirect('prospecta:opportunities_list')

    meetings = opportunity.meetings.all()

    context.update({
        'opportunity': opportunity,
        'meetings': meetings,
    })

    return render(request, 'prospecta/meetings/list.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def create_meeting(request, pk):
    """Criar reunião para oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    context = get_user_context(request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        meeting_type = request.POST.get('meeting_type', 'virtual')
        start_datetime = request.POST.get('start_datetime')
        end_datetime = request.POST.get('end_datetime')
        location = request.POST.get('location', '')
        attendee_ids = request.POST.getlist('attendees')

        if not title or not start_datetime or not end_datetime:
            messages.error(
                request, 'Título, data/hora de início e fim são obrigatórios.')
            return redirect('prospecta:opportunity_meetings', pk=pk)

        # Converter strings para datetime
        start_dt = datetime.fromisoformat(start_datetime)
        end_dt = datetime.fromisoformat(end_datetime)

        meeting = Meeting.objects.create(
            opportunity=opportunity,
            title=title,
            description=description,
            meeting_type=meeting_type,
            start_datetime=start_dt,
            end_datetime=end_dt,
            location=location,
            organizer=request.user
        )

        # Adicionar participantes
        if attendee_ids:
            attendees = User.objects.filter(id__in=attendee_ids)
            meeting.attendees.set(attendees)

        messages.success(request, f'Reunião "{title}" criada com sucesso!')

        # Signal irá sincronizar automaticamente com Google Calendar

        return redirect('prospecta:opportunity_meetings', pk=pk)

    # GET - mostrar formulário
    users = User.objects.filter(profile__is_active=True)
    context.update({
        'opportunity': opportunity,
        'users': users,
    })

    return render(request, 'prospecta/meetings/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def edit_meeting(request, pk):
    """Editar reunião"""
    meeting = get_object_or_404(Meeting, pk=pk)
    context = get_user_context(request.user)

    # Verificar permissão
    profile = request.user.profile
    if not profile.is_admin() and meeting.organizer != request.user:
        messages.error(
            request, 'Você não tem permissão para editar esta reunião.')
        return redirect('prospecta:opportunity_meetings', pk=meeting.opportunity.pk)

    if request.method == 'POST':
        meeting.title = request.POST.get('title')
        meeting.description = request.POST.get('description', '')
        meeting.meeting_type = request.POST.get('meeting_type', 'virtual')
        meeting.status = request.POST.get('status', 'agendada')
        meeting.location = request.POST.get('location', '')

        start_datetime = request.POST.get('start_datetime')
        end_datetime = request.POST.get('end_datetime')

        if start_datetime:
            meeting.start_datetime = datetime.fromisoformat(start_datetime)
        if end_datetime:
            meeting.end_datetime = datetime.fromisoformat(end_datetime)

        attendee_ids = request.POST.getlist('attendees')
        if attendee_ids:
            attendees = User.objects.filter(id__in=attendee_ids)
            meeting.attendees.set(attendees)

        meeting.save()

        messages.success(request, 'Reunião atualizada com sucesso!')
        return redirect('prospecta:opportunity_meetings', pk=meeting.opportunity.pk)

    # GET - mostrar formulário
    users = User.objects.filter(profile__is_active=True)
    context.update({
        'meeting': meeting,
        'opportunity': meeting.opportunity,
        'users': users,
    })

    return render(request, 'prospecta/meetings/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def delete_meeting(request, pk):
    """Deletar reunião"""
    meeting = get_object_or_404(Meeting, pk=pk)
    opportunity_pk = meeting.opportunity.pk

    # Verificar permissão
    profile = request.user.profile
    if not profile.is_admin() and meeting.organizer != request.user:
        messages.error(
            request, 'Você não tem permissão para deletar esta reunião.')
        return redirect('prospecta:opportunity_meetings', pk=opportunity_pk)

    meeting_title = meeting.title
    meeting.delete()  # Pre-delete signal irá remover do Google Calendar
    messages.success(
        request, f'Reunião "{meeting_title}" deletada com sucesso!')

    return redirect('prospecta:opportunity_meetings', pk=opportunity_pk)


# ============================================================================
# INTEGRAÇÃO GOOGLE CALENDAR
# ============================================================================

@login_required(login_url='account_login')
def google_calendar_callback(request):
    """Callback OAuth do Google Calendar"""
    # TODO: Implementar OAuth flow completo
    # 1. Receber code do Google
    # 2. Trocar code por access_token e refresh_token
    # 3. Salvar tokens no GoogleCalendarIntegration
    # 4. Redirecionar usuário

    code = request.GET.get('code')

    if not code:
        messages.error(request, 'Erro na autenticação com Google.')
        return redirect('prospecta:dashboard')

    # Por enquanto, apenas placeholder
    messages.info(
        request, 'Integração com Google Calendar em desenvolvimento.')
    return redirect('prospecta:dashboard')


# ============================================================================
# ASSOCIAR REUNIÃO A ATIVIDADE
# ============================================================================

@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def associate_meeting_to_activity(request, activity_pk):
    """Associar uma reunião a uma atividade"""
    activity = get_object_or_404(Activity, pk=activity_pk)

    if request.method == 'POST':
        meeting_id = request.POST.get('meeting_id')

        if meeting_id:
            try:
                meeting = Meeting.objects.get(pk=meeting_id)
                # Verificar se a reunião pertence à mesma oportunidade
                if meeting.opportunity == activity.stage.opportunity:
                    activity.meeting = meeting
                    activity.save()
                    messages.success(
                        request, f'Reunião "{meeting.title}" associada à atividade!')
                else:
                    messages.error(
                        request, 'A reunião não pertence à mesma oportunidade.')
            except Meeting.DoesNotExist:
                messages.error(request, 'Reunião não encontrada.')
        else:
            activity.meeting = None
            activity.save()
            messages.success(request, 'Reunião desassociada da atividade.')

        return redirect('prospecta:activity_detail', pk=activity_pk)

    # GET - mostrar formulário
    opportunity = activity.stage.opportunity
    meetings = opportunity.meetings.all()

    context = get_user_context(request.user)
    context.update({
        'activity': activity,
        'opportunity': opportunity,
        'meetings': meetings,
        'current_meeting': activity.meeting,
    })

    return render(request, 'prospecta/meetings/associate_to_activity.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def activity_quick_associate(request, activity_pk):
    """Quick associate meeting via AJAX/modal"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    activity = get_object_or_404(Activity, pk=activity_pk)
    opportunity = activity.stage.opportunity
    meeting_id = request.POST.get('meeting_id')

    try:
        if meeting_id:
            meeting = Meeting.objects.get(pk=meeting_id)
            if meeting.opportunity != opportunity:
                return JsonResponse({'error': 'Reunião não pertence a esta oportunidade'}, status=400)
            activity.meeting = meeting
        else:
            activity.meeting = None

        activity.save()

        return JsonResponse({
            'success': True,
            'message': 'Associação atualizada com sucesso',
            'meeting': {
                'id': str(activity.meeting.id) if activity.meeting else None,
                'title': activity.meeting.title if activity.meeting else None,
            }
        })
    except Meeting.DoesNotExist:
        return JsonResponse({'error': 'Reunião não encontrada'}, status=404)
