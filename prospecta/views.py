from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib import messages

from .models import (
    UserProfile, Client, Contact, SalesModel, Opportunity,
    Stage, Activity, OpportunityHistory, StageHistory, ActivityHistory,
    OpportunityParticipant, Notification, ActivityComment,
    ActivityAttachment, OpportunityDocument, OpportunityCustomValue,
    OpportunityStatus
)
from .utils import get_user_context, permission_required, permissions_required_all
from .notifications import (
    notify_activity_assigned, notify_activity_reassigned,
    notify_activity_submitted_for_verification, notify_activity_approved,
    notify_activity_rejected, notify_activity_comment,
    get_unread_notifications_count, get_recent_notifications, mark_all_as_read
)


# ============================================================================
# Decorators and helpers
# ============================================================================

def role_required(*roles):
    """
    Decorator para verificar role do usuário.
    DEPRECADO: Use @permission_required('Nome da Permissão') de utils.py
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                try:
                    profile = request.user.profile
                    if profile.role in roles or profile.is_admin():
                        return view_func(request, *args, **kwargs)
                except UserProfile.DoesNotExist:
                    pass
            return redirect('account_login')
        return wrapper
    return decorator


def write_permission_required(view_func):
    """
    Decorator para verificar permissão de escrita (visitantes não podem).
    DEPRECADO: Use @permission_required('Criar/Editar ...') de utils.py
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                if profile.can_write():
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(
                        request, 'Visitantes não têm permissão para realizar esta ação.')
                    return redirect('prospecta:dashboard')
            except UserProfile.DoesNotExist:
                pass
        return redirect('account_login')
    return wrapper


# NOTA: get_user_context foi movido para utils.py
# Importado acima: from .utils import get_user_context


# ============================================================================
# Public Pages
# ============================================================================

def home(request):
    """Página inicial do sistema"""
    context = get_user_context(request.user)

    if request.user.is_authenticated:
        # Dados do dashboard para usuários autenticados
        context.update({
            'total_opportunities': Opportunity.objects.count(),
            'total_clients': Client.objects.count(),
            'open_opportunities': Opportunity.objects.filter(status__in=['em_andamento', 'atrasada']).count(),
            'my_activities': Activity.objects.filter(
                assigned_to=request.user,
                status='pendente'
            ).count(),
        })

    return render(request, 'prospecta/home.html', context)


# ============================================================================
# Dashboard and Profile
# ============================================================================

@login_required(login_url='account_login')
def dashboard(request):
    """Dashboard principal do sistema com KPIs e análises"""
    context = get_user_context(request.user)

    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Se o usuário não tem perfil, criar um padrão
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Dados baseados no role do usuário
    # Todos veem tudo, EXCETO visitantes que veem apenas suas próprias oportunidades
    if profile.is_visitor():
        # Visitante vê apenas suas próprias oportunidades e atividades
        opportunities = Opportunity.objects.filter(
            Q(created_by=request.user) | Q(responsible_user=request.user)
        )
        activities = Activity.objects.filter(assigned_to=request.user)
        users = None
    else:
        # Admin, Gerente e Analista veem tudo
        opportunities = Opportunity.objects.all()
        activities = Activity.objects.all()
        users = User.objects.all() if profile.is_admin() else None

    # KPIs - Oportunidades
    total_opportunities = opportunities.count()
    open_opportunities_count = opportunities.filter(
        status='aberta').count()
    delayed_opportunities = opportunities.filter(status='atrasada').count()
    won_opportunities = opportunities.filter(status='ganha').count()
    lost_opportunities = opportunities.filter(status='perdida').count()
    suspended_opportunities = opportunities.filter(status='suspensa').count()
    canceled_opportunities = opportunities.filter(status='cancelada').count()

    # Valores
    total_pipeline = opportunities.aggregate(
        Sum('value_brl'))['value_brl__sum'] or 0
    won_value = opportunities.filter(status='ganha').aggregate(
        Sum('value_brl'))['value_brl__sum'] or 0
    active_value = opportunities.filter(status__in=['aberta', 'atrasada']).aggregate(
        Sum('value_brl'))['value_brl__sum'] or 0

    # Taxa de conversão
    conversion_rate = (won_opportunities / total_opportunities *
                       100) if total_opportunities > 0 else 0

    # Atividades
    pending_activities = activities.filter(status='pendente').count()
    in_progress_activities = activities.filter(status='em_progresso').count()
    blocked_activities = activities.filter(status='bloqueada').count()
    completed_activities = activities.filter(status='concluída').count()

    # Atividades pendentes de aprovação
    activities_pending_approval = activities.filter(
        status='aguardando_aprovacao'
    ).count()

    # Oportunidades recentes
    recent_opportunities = opportunities.order_by('-created_at')[:5]

    # Próximas atividades (próximos 7 dias)
    today = timezone.now()
    next_week = today + timedelta(days=7)
    upcoming_activities = activities.filter(
        status__in=['pendente', 'em_progresso'],
        created_at__lte=next_week
    ).order_by('created_at')[:5]

    # Status do pipeline (por status)
    pipeline_by_status = {
        'aberta': open_opportunities_count,
        'atrasada': delayed_opportunities,
        'ganha': won_opportunities,
        'perdida': lost_opportunities,
        'suspensa': suspended_opportunities,
        'cancelada': canceled_opportunities,
    }

    # Dados para gráfico de distribuição
    status_distribution = []
    for status, count in pipeline_by_status.items():
        percentage = (count / total_opportunities *
                      100) if total_opportunities > 0 else 0
        status_distribution.append({
            'status': status.replace('_', ' ').title(),
            'count': count,
            'percentage': round(percentage, 1),
            'value': opportunities.filter(status=status).aggregate(Sum('value_brl'))['value_brl__sum'] or 0,
        })

    # Cálculos de dashboard
    context.update({
        # Contagens
        'total_opportunities': total_opportunities,
        'open_opportunities': open_opportunities_count + delayed_opportunities,
        'open_opportunities_count': open_opportunities_count,
        'delayed_opportunities': delayed_opportunities,
        'won_opportunities': won_opportunities,
        'lost_opportunities': lost_opportunities,
        'suspended_opportunities': suspended_opportunities,
        'canceled_opportunities': canceled_opportunities,
        'opportunities_count': total_opportunities,

        # Valores
        'total_pipeline': total_pipeline,
        'won_value': won_value,
        'in_progress_value': active_value,
        'conversion_rate': round(conversion_rate, 1),

        # Atividades
        'activities_count': activities.count(),
        'pending_activities': pending_activities,
        'in_progress_activities': in_progress_activities,
        'blocked_activities': blocked_activities,
        'completed_activities': completed_activities,
        'activities_pending_approval': activities_pending_approval,

        # Listas
        'recent_opportunities': recent_opportunities,
        'upcoming_activities': upcoming_activities,
        'pipeline_status_distribution': status_distribution,
    })

    if profile.is_admin() and users:
        context['users_count'] = users.count()
        context['active_users'] = users.filter(profile__is_active=True).count()

    return render(request, 'prospecta/dashboard.html', context)


@login_required(login_url='account_login')
def profile_view(request):
    """Página de perfil do usuário"""
    context = get_user_context(request.user)

    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    context['profile'] = profile

    if request.method == 'POST':
        try:
            # Atualizar campos simples
            profile.department = request.POST.get('department') or ''
            profile.phone = request.POST.get('phone') or ''
            profile.bio = request.POST.get('bio') or ''

            # Processar upload de avatar se fornecido
            if 'avatar' in request.FILES and request.FILES['avatar']:
                profile.avatar = request.FILES['avatar']

            profile.save()
            messages.success(request, '✓ Perfil atualizado com sucesso!')
        except Exception as e:
            messages.error(request, f'✗ Erro ao atualizar perfil: {str(e)}')

        return redirect('prospecta:profile')

    return render(request, 'prospecta/profile.html', context)


# ============================================================================
# Opportunities Management
# ============================================================================

@login_required(login_url='account_login')
def opportunities_list(request):
    """Lista de oportunidades com filtros"""
    context = get_user_context(request.user)

    # Visitantes não podem acessar oportunidades
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if profile.is_visitor():
        messages.error(
            request, 'Você não tem permissão para acessar oportunidades.')
        return redirect('prospecta:home')

    # Todos veem tudo (exceto visitantes que já foram redirecionados)
    opportunities = Opportunity.objects.all()

    # Aplicar filtros
    status = request.GET.get('status')
    if status:
        opportunities = opportunities.filter(status=status)

    client_id = request.GET.get('client')
    if client_id:
        opportunities = opportunities.filter(client_id=client_id)

    estagio = request.GET.get('estagio')
    if estagio:
        opportunities = opportunities.filter(estagio=estagio)

    fase = request.GET.get('fase')
    if fase:
        opportunities = opportunities.filter(fase=fase)

    # Ordenação
    sort = request.GET.get('sort', '-created_at')
    opportunities = opportunities.order_by(sort)

    context.update({
        'opportunities': opportunities,
        'clients': Client.objects.all(),
        'status_choices': Opportunity.STATUS_CHOICES,
        'opportunity_statuses': OpportunityStatus.objects.filter(is_active=True),
        'estagio_choices': Opportunity.ESTAGIO_CHOICES,
        'fase_choices': Opportunity.FASE_CHOICES,
    })

    return render(request, 'prospecta/opportunities/list.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def opportunity_create(request):
    """Criar nova oportunidade"""
    context = get_user_context(request.user)

    if request.method == 'POST':
        # Tratar valor decimal vazio - valor é inserido em milhões (MM)
        value_brl = request.POST.get('value_brl')
        if value_brl == '' or value_brl is None:
            value_brl = None
        else:
            try:
                # Converter de milhões para valor real
                from decimal import Decimal
                value_brl = Decimal(value_brl) * Decimal('1000000')
            except:
                value_brl = None

        # Tratar estagio e fase vazios
        estagio = request.POST.get('estagio') or None
        fase = request.POST.get('fase') or None

        opportunity = Opportunity(
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            notes=request.POST.get('notes', ''),
            produto=request.POST.get('produto', ''),
            client_id=request.POST['client'],
            created_by=request.user,
            responsible_user_id=request.POST.get(
                'responsible_user', request.user.id),
            sales_model_id=request.POST.get('sales_model'),
            value_brl=value_brl,
            estagio=estagio,
            fase=fase,
            expected_delivery_date=request.POST.get(
                'expected_delivery_date') or None,
        )
        opportunity.save()

        # Adicionar parcerias (ManyToMany precisa ser salvo após o objeto)
        partnerships_ids = request.POST.getlist('partnerships')
        if partnerships_ids:
            opportunity.partnerships.set(partnerships_ids)

        # Processar valores customizados
        new_labels = request.POST.getlist('new_value_label[]')
        new_amounts = request.POST.getlist('new_value_amount[]')
        
        for i, (label, amount) in enumerate(zip(new_labels, new_amounts)):
            if label and amount:
                try:
                    OpportunityCustomValue.objects.create(
                        opportunity=opportunity,
                        label=label.strip(),
                        value=amount,
                        order=i
                    )
                except (ValueError, TypeError):
                    pass

        # Processar arquivos anexados
        files = request.FILES.getlist('documents')
        for file in files:
            OpportunityDocument.objects.create(
                opportunity=opportunity,
                title=file.name,
                document_type='outro',
                file=file,
                uploaded_by=request.user,
            )

        # Criar histórico
        partnerships_names = ', '.join(
            [c.name for c in opportunity.partnerships.all()])
        history_details = f'Oportunidade criada por {request.user.get_full_name()}'
        if partnerships_names:
            history_details += f' com parcerias: {partnerships_names}'
        if files:
            history_details += f'. {len(files)} documento(s) anexado(s)'
        
        # Adicionar informação sobre valores customizados
        custom_values_count = opportunity.custom_values.count()
        if custom_values_count > 0:
            history_details += f'. {custom_values_count} valor(es) adicional(is) cadastrado(s)'

        OpportunityHistory.objects.create(
            opportunity=opportunity,
            changed_by=request.user,
            change_type='criacao',
            change_details=history_details
        )

        messages.success(request, 'Oportunidade criada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=opportunity.pk)

    context.update({
        'clients': Client.objects.all(),
        'sales_models': SalesModel.objects.all(),
        'users': User.objects.filter(profile__is_active=True).order_by('first_name', 'last_name'),
        'selected_client': request.GET.get('client', ''),
        'estagio_choices': Opportunity.ESTAGIO_CHOICES,
        'fase_choices': Opportunity.FASE_CHOICES,
    })

    return render(request, 'prospecta/opportunities/form.html', context)


@login_required(login_url='account_login')
def opportunity_detail(request, pk):
    """Detalhes da oportunidade"""
    """Detalhes de uma oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)

    # Verificar permissão - visitantes não podem ver detalhes
    try:
        profile = request.user.profile
        if profile.is_visitor():
            messages.error(
                request, 'Você não tem permissão para ver detalhes de oportunidades.')
            return redirect('prospecta:home')
    except UserProfile.DoesNotExist:
        return redirect('account_login')

    # Listar usuários disponíveis para adicionar como participantes
    current_participants = opportunity.participants.values_list(
        'user_id', flat=True)
    available_users = User.objects.filter(
        profile__is_active=True
    ).exclude(id__in=current_participants)

    # Contar atividades
    opportunity_activity_count = Activity.objects.filter(
        stage__opportunity=opportunity
    ).count()

    # Buscar histórico de atividades relacionadas à oportunidade
    activity_history = ActivityHistory.objects.filter(
        activity__stage__opportunity=opportunity
    ).select_related('activity', 'changed_by')

    context = get_user_context(request.user)
    context.update({
        'opportunity': opportunity,
        'stages': opportunity.stages.all().order_by('order'),
        'history': opportunity.history.all()[:10],
        'activity_history': activity_history,
        'available_users': available_users,
        'opportunity_activity_count': opportunity_activity_count,
        'status_choices': Opportunity.STATUS_CHOICES,
        'opportunity_statuses': OpportunityStatus.objects.filter(is_active=True),
    })

    return render(request, 'prospecta/opportunities/detail.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def opportunity_update(request, pk):
    """Editar oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)

    if request.method == 'POST':
        # Tratar valor decimal - valor é inserido em milhões (MM)
        value_brl = request.POST.get('value_brl', '').strip()
        if value_brl == '':
            # Manter o valor original se o campo estiver vazio
            value_brl = opportunity.value_brl
        else:
            # Converter de milhões para valor real
            try:
                from decimal import Decimal
                value_brl = Decimal(value_brl) * Decimal('1000000')
            except:
                value_brl = opportunity.value_brl

        opportunity.title = request.POST['title']
        opportunity.description = request.POST.get('description', '')
        opportunity.notes = request.POST.get('notes', '')
        opportunity.produto = request.POST.get('produto', '')
        opportunity.client_id = request.POST['client']
        opportunity.responsible_user_id = request.POST['responsible_user']
        opportunity.sales_model_id = request.POST.get('sales_model') or None
        opportunity.value_brl = value_brl
        opportunity.estagio = request.POST.get('estagio') or None
        opportunity.fase = request.POST.get('fase') or None
        opportunity.expected_delivery_date = request.POST.get(
            'expected_delivery_date') or None
        opportunity.status = request.POST.get('status', opportunity.status)
        opportunity.save()

        # Atualizar parcerias
        partnerships_ids = request.POST.getlist('partnerships')
        opportunity.partnerships.set(partnerships_ids)

        # Processar valores customizados a serem deletados
        delete_ids = request.POST.getlist('delete_value_id[]')
        if delete_ids:
            OpportunityCustomValue.objects.filter(
                id__in=delete_ids,
                opportunity=opportunity
            ).delete()

        # Processar valores customizados existentes (atualizar)
        existing_ids = request.POST.getlist('existing_value_id[]')
        existing_labels = request.POST.getlist('existing_value_label[]')
        existing_amounts = request.POST.getlist('existing_value_amount[]')
        
        for value_id, label, amount in zip(existing_ids, existing_labels, existing_amounts):
            if value_id and label and amount:
                try:
                    custom_value = OpportunityCustomValue.objects.get(
                        id=value_id,
                        opportunity=opportunity
                    )
                    custom_value.label = label.strip()
                    custom_value.value = amount
                    custom_value.save()
                except (OpportunityCustomValue.DoesNotExist, ValueError, TypeError):
                    pass

        # Processar novos valores customizados
        new_labels = request.POST.getlist('new_value_label[]')
        new_amounts = request.POST.getlist('new_value_amount[]')
        
        # Calcular próxima ordem
        max_order = opportunity.custom_values.count()
        
        for i, (label, amount) in enumerate(zip(new_labels, new_amounts)):
            if label and amount:
                try:
                    OpportunityCustomValue.objects.create(
                        opportunity=opportunity,
                        label=label.strip(),
                        value=amount,
                        order=max_order + i
                    )
                except (ValueError, TypeError):
                    pass

        # Criar histórico
        partnerships_names = ', '.join(
            [c.name for c in opportunity.partnerships.all()])
        history_details = f'Oportunidade atualizada por {request.user.get_full_name()}'
        if partnerships_names:
            history_details += f' - Parcerias: {partnerships_names}'
        
        # Adicionar informação sobre valores customizados
        custom_values_count = opportunity.custom_values.count()
        if custom_values_count > 0:
            history_details += f' - {custom_values_count} valor(es) adicional(is)'

        OpportunityHistory.objects.create(
            opportunity=opportunity,
            changed_by=request.user,
            change_type='atualizacao',
            change_details=history_details
        )

        messages.success(request, 'Oportunidade atualizada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=opportunity.pk)

    context = get_user_context(request.user)
    context.update({
        'opportunity': opportunity,
        'clients': Client.objects.all(),
        'sales_models': SalesModel.objects.all(),
        'users': User.objects.filter(profile__is_active=True).order_by('first_name', 'last_name'),
        'status_choices': Opportunity.STATUS_CHOICES,
        'opportunity_statuses': OpportunityStatus.objects.filter(is_active=True),
        'estagio_choices': Opportunity.ESTAGIO_CHOICES,
        'fase_choices': Opportunity.FASE_CHOICES,
    })

    return render(request, 'prospecta/opportunities/form.html', context)


@login_required(login_url='account_login')
@role_required('admin')
def opportunity_delete(request, pk):
    """Deletar oportunidade - apenas administradores"""
    opportunity = get_object_or_404(Opportunity, pk=pk)

    if request.method == 'POST':
        opportunity.delete()
        messages.success(request, 'Oportunidade deletada com sucesso!')
        return redirect('prospecta:opportunities_list')

    context = get_user_context(request.user)
    context['opportunity'] = opportunity

    return render(request, 'prospecta/opportunities/confirm_delete.html', context)


@login_required(login_url='account_login')
@require_http_methods(['GET'])
def opportunities_filter(request):
    """HTMX endpoint para filtrar oportunidades"""
    try:
        profile = request.user.profile
        if profile.is_visitor():
            return HttpResponse('')
    except UserProfile.DoesNotExist:
        return HttpResponse('')

    # Todos veem tudo (exceto visitantes)
    opportunities = Opportunity.objects.all()

    status = request.GET.get('status')
    if status:
        opportunities = opportunities.filter(status=status)

    client_id = request.GET.get('client')
    if client_id:
        opportunities = opportunities.filter(client_id=client_id)

    estagio = request.GET.get('estagio')
    if estagio:
        opportunities = opportunities.filter(estagio=estagio)

    fase = request.GET.get('fase')
    if fase:
        opportunities = opportunities.filter(fase=fase)

    return render(request, 'prospecta/components/opportunities_table.html', {
        'opportunities': opportunities,
        'opportunity_statuses': OpportunityStatus.objects.filter(is_active=True),
    })


@login_required(login_url='account_login')
@require_http_methods(['POST'])
def opportunity_status_update(request, pk):
    """HTMX endpoint para atualizar status da oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    new_status = request.POST.get('status')

    # Verificar se o status é válido (nos status padrão ou nos status customizados)
    valid_default_statuses = dict(Opportunity.STATUS_CHOICES).keys()
    valid_custom_statuses = OpportunityStatus.objects.filter(is_active=True).values_list('slug', flat=True)
    
    if new_status in valid_default_statuses or new_status in valid_custom_statuses:
        old_status = opportunity.status
        opportunity.status = new_status
        opportunity.save()

        # Tentar obter o nome do status para o histórico
        status_name = new_status
        status_obj = OpportunityStatus.objects.filter(slug=new_status).first()
        if status_obj:
            status_name = status_obj.name
        else:
            # Fallback para status padrão
            status_name = dict(Opportunity.STATUS_CHOICES).get(new_status, new_status)

        OpportunityHistory.objects.create(
            opportunity=opportunity,
            changed_by=request.user,
            change_type='atualizacao_status',
            change_details=f'Status alterado para {status_name} por {request.user.get_full_name()}'
        )

    return render(request, 'prospecta/components/opportunity_badge.html', {
        'opportunity': opportunity,
        'opportunity_statuses': OpportunityStatus.objects.filter(is_active=True),
    })


# ============================================================================
# Clients Management
# ============================================================================

@login_required(login_url='account_login')
def clients_list(request):
    """Lista de empresas"""
    context = get_user_context(request.user)

    # Visitantes não podem acessar empresas
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if profile.is_visitor():
        messages.error(
            request, 'Você não tem permissão para acessar empresas.')
        return redirect('prospecta:home')

    clients = Client.objects.all()

    search = request.GET.get('search')
    if search:
        clients = clients.filter(
            Q(name__icontains=search) | Q(razao_social__icontains=search) | Q(
                cnpj__icontains=search) | Q(email__icontains=search)
        )

    context['clients'] = clients.order_by('name')
    return render(request, 'prospecta/clients/list.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def client_create(request):
    """Criar nova empresa"""
    context = get_user_context(request.user)

    if request.method == 'POST':
        client = Client(
            name=request.POST['name'],
            razao_social=request.POST.get('razao_social', '') or None,
            cnpj=request.POST.get('cnpj', '') or None,
            address=request.POST.get('address', ''),
            phone=request.POST.get('phone', ''),
            email=request.POST.get('email', ''),
        )
        client.save()
        messages.success(request, 'Empresa criada com sucesso!')
        return redirect('prospecta:client_detail', pk=client.pk)

    return render(request, 'prospecta/clients/form.html', context)


@login_required(login_url='account_login')
def client_detail(request, pk):
    """Detalhes da empresa"""
    # Visitantes não podem acessar
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if profile.is_visitor():
        messages.error(
            request, 'Você não tem permissão para acessar empresas.')
        return redirect('prospecta:home')
    client = get_object_or_404(Client, pk=pk)
    context = get_user_context(request.user)
    context.update({
        'client': client,
        'contacts': client.contacts.all(),
        'opportunities': client.opportunities.all(),
    })

    return render(request, 'prospecta/clients/detail.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def client_update(request, pk):
    """Editar empresa"""
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        client.name = request.POST['name']
        client.razao_social = request.POST.get('razao_social', '') or None
        client.cnpj = request.POST.get('cnpj', '') or None
        client.address = request.POST.get('address', '')
        client.phone = request.POST.get('phone', '')
        client.email = request.POST.get('email', '')
        client.save()
        messages.success(request, 'Empresa atualizada com sucesso!')
        return redirect('prospecta:client_detail', pk=client.pk)

    context = get_user_context(request.user)
    context['client'] = client

    return render(request, 'prospecta/clients/form.html', context)


# ============================================================================
# Activities Management
# ============================================================================

@login_required(login_url='account_login')
def activities_list(request):
    """Lista de atividades do usuário"""
    context = get_user_context(request.user)

    # Visitantes não podem acessar atividades
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if profile.is_visitor():
        messages.error(
            request, 'Você não tem permissão para acessar atividades.')
        return redirect('prospecta:home')

    # Todos veem tudo (exceto visitantes que já foram redirecionados)
    activities = Activity.objects.all().select_related(
        'stage', 'stage__opportunity', 'assigned_to', 'delegated_by', 'verifier'
    )

    status = request.GET.get('status')
    if status:
        activities = activities.filter(status=status)

    # Obter tipo de visualização (tabela ou hierarquia)
    view_type = request.GET.get('view', 'table')

    # Criar estrutura hierárquica: Oportunidade -> Etapa -> Atividades
    hierarchy = {}
    for activity in activities.order_by('stage__opportunity__title', 'stage__order', '-created_at'):
        opportunity = activity.stage.opportunity
        stage = activity.stage
        
        if opportunity.pk not in hierarchy:
            hierarchy[opportunity.pk] = {
                'opportunity': opportunity,
                'stages': {}
            }
        
        if stage.pk not in hierarchy[opportunity.pk]['stages']:
            hierarchy[opportunity.pk]['stages'][stage.pk] = {
                'stage': stage,
                'activities': []
            }
        
        hierarchy[opportunity.pk]['stages'][stage.pk]['activities'].append(activity)

    context.update({
        'activities': activities.order_by('-created_at'),
        'pending_count': activities.filter(status='pendente').count(),
        'status_choices': Activity.STATUS_CHOICES,
        'view_type': view_type,
        'hierarchy': hierarchy,
    })

    return render(request, 'prospecta/activities/list.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def activity_approve(request, pk):
    """Aprovar atividade"""
    activity = get_object_or_404(Activity, pk=pk)

    if request.method == 'POST':
        activity.approved = True
        activity.approval_date = datetime.now()
        activity.status = 'concluida'
        activity.save()

        ActivityHistory.objects.create(
            activity=activity,
            changed_by=request.user,
            change_type='aprovacao',
            change_details=f'Atividade aprovada por {request.user.get_full_name()}'
        )

        messages.success(request, 'Atividade aprovada com sucesso!')
        return redirect('prospecta:activities_list')

    context = get_user_context(request.user)
    context['activity'] = activity

    return render(request, 'prospecta/activities/confirm_approve.html', context)


# ============================================================================
# Reports
# ============================================================================

@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def reports(request):
    """Página de relatórios"""
    context = get_user_context(request.user)

    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Dados para relatórios - todos veem tudo (exceto visitantes via decorator)
    if profile.is_visitor():
        opportunities = Opportunity.objects.filter(
            Q(created_by=request.user) | Q(responsible_user=request.user)
        )
    else:
        opportunities = Opportunity.objects.all()

    # Contar oportunidades por status
    total_opp = opportunities.count()
    won_opp = opportunities.filter(status='ganha').count()
    lost_opp = opportunities.filter(status='perdida').count()
    open_opp = opportunities.filter(status__in=['aberta', 'atrasada']).count()

    # Valores
    total_value = opportunities.aggregate(Sum('value_brl'))[
        'value_brl__sum'] or 0
    won_value = opportunities.filter(status='ganha').aggregate(
        Sum('value_brl'))['value_brl__sum'] or 0

    # Calcular percentuais com proteção contra divisão por zero
    if total_opp > 0:
        conversion_rate = (won_opp * 100) / total_opp
        loss_rate = (lost_opp * 100) / total_opp
        open_percent = (open_opp * 100) / total_opp
        won_percent = (won_opp * 100) / total_opp
        lost_percent = (lost_opp * 100) / total_opp
        average_value = total_value / total_opp
    else:
        conversion_rate = 0
        loss_rate = 0
        open_percent = 0
        won_percent = 0
        lost_percent = 0
        average_value = 0

    # Estatísticas
    context.update({
        'total_opportunities': total_opp,
        'won_opportunities': won_opp,
        'lost_opportunities': lost_opp,
        'open_opportunities': open_opp,
        'total_value': total_value,
        'won_value': won_value,
        'conversion_rate': conversion_rate,
        'loss_rate': loss_rate,
        'open_percent': open_percent,
        'won_percent': won_percent,
        'lost_percent': lost_percent,
        'average_value': average_value,
    })

    return render(request, 'prospecta/reports.html', context)


# ============================================================================
# STAGES (Etapas de Oportunidade)
# ============================================================================

@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def stage_create(request, opportunity_pk):
    """Criar nova etapa em uma oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=opportunity_pk)
    context = get_user_context(request.user)

    if request.method == 'POST':
        responsible_user_id = request.POST.get('responsible_user')
        stage = Stage(
            opportunity=opportunity,
            name=request.POST['name'],
            order=request.POST.get('order', 1),
            responsible_user_id=responsible_user_id if responsible_user_id else None,
            created_by=request.user,
        )
        stage.save()

        responsible_name = stage.responsible_user.get_full_name() if stage.responsible_user else 'Não definido'
        StageHistory.objects.create(
            stage=stage,
            changed_by=request.user,
            change_type='criacao',
            change_details=f'Etapa criada por {request.user.get_full_name()}. Responsável: {responsible_name}'
        )

        messages.success(request, 'Etapa criada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=opportunity.pk)

    context['opportunity'] = opportunity
    context['users'] = User.objects.filter(profile__is_active=True).order_by('first_name', 'last_name')
    return render(request, 'prospecta/stages/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def stage_update(request, pk):
    """Editar etapa"""
    stage = get_object_or_404(Stage, pk=pk)

    if request.method == 'POST':
        old_responsible = stage.responsible_user
        stage.name = request.POST['name']
        stage.order = request.POST.get('order', stage.order)
        responsible_user_id = request.POST.get('responsible_user')
        stage.responsible_user_id = responsible_user_id if responsible_user_id else None
        stage.save()

        # Montar detalhes da mudança
        details = f'Etapa atualizada por {request.user.get_full_name()}'
        if old_responsible != stage.responsible_user:
            old_name = old_responsible.get_full_name() if old_responsible else 'Não definido'
            new_name = stage.responsible_user.get_full_name() if stage.responsible_user else 'Não definido'
            details += f'. Responsável alterado de "{old_name}" para "{new_name}"'

        StageHistory.objects.create(
            stage=stage,
            changed_by=request.user,
            change_type='atualizacao',
            change_details=details
        )

        messages.success(request, 'Etapa atualizada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=stage.opportunity.pk)

    context = get_user_context(request.user)
    context['stage'] = stage
    context['users'] = User.objects.filter(profile__is_active=True).order_by('first_name', 'last_name')
    return render(request, 'prospecta/stages/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def stage_delete(request, pk):
    """Deletar etapa"""
    stage = get_object_or_404(Stage, pk=pk)
    opportunity_pk = stage.opportunity.pk

    if request.method == 'POST':
        stage.delete()
        messages.success(request, 'Etapa deletada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=opportunity_pk)

    context = get_user_context(request.user)
    context['stage'] = stage
    return render(request, 'prospecta/stages/confirm_delete.html', context)


# ============================================================================
# ACTIVITIES (Atividades dentro de Etapas)
# ============================================================================

@login_required(login_url='account_login')
def activity_detail(request, pk):
    """Página de detalhes de uma atividade com histórico e comentários"""
    activity = get_object_or_404(Activity, pk=pk)
    context = get_user_context(request.user)

    # Verificar se o usuário tem permissão para ver
    allowed = (
        activity.assigned_to == request.user or
        activity.verifier == request.user or
        activity.delegated_by == request.user or
        context.get('is_admin') or
        context.get('is_manager')
    )

    if not allowed:
        messages.error(
            request, 'Você não tem permissão para ver esta atividade.')
        return redirect('prospecta:activities_list')

    # Obter comentários e histórico
    comments = activity.comments.all().order_by('created_at')
    history = ActivityHistory.objects.filter(
        activity=activity).order_by('-changed_at')[:20]

    context.update({
        'activity': activity,
        'comments': comments,
        'history': history,
        'can_submit': activity.assigned_to == request.user and activity.can_be_submitted_for_verification(),
        'can_verify': (activity.verifier == request.user or context.get('is_admin')) and activity.can_be_verified(),
        'can_comment': allowed,
    })
    return render(request, 'prospecta/activities/detail.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def activity_create_standalone(request):
    """Criar nova atividade standalone (escolhendo oportunidade/etapa)"""
    context = get_user_context(request.user)

    # Obter oportunidades com suas etapas
    if context.get('is_admin') or context.get('is_manager'):
        opportunities = Opportunity.objects.filter(
            status__in=['aberta', 'atrasada', 'suspensa']
        ).select_related('client', 'responsible_user').prefetch_related('stages')
    else:
        opportunities = Opportunity.objects.filter(
            status__in=['aberta', 'atrasada', 'suspensa'],
            responsible_user=request.user
        ).select_related('client', 'responsible_user').prefetch_related('stages')

    if request.method == 'POST':
        stage_id = request.POST.get('stage')
        if not stage_id:
            messages.error(request, 'Selecione uma etapa para a atividade.')
            context.update({
                'opportunities': opportunities,
                'users': User.objects.filter(profile__is_active=True).order_by('first_name', 'last_name'),
                'activity_type_choices': Activity.ACTIVITY_TYPE_CHOICES,
            })
            return render(request, 'prospecta/activities/form_standalone.html', context)

        stage = get_object_or_404(Stage, pk=stage_id)
        assigned_to_id = request.POST.get('assigned_to') or None

        activity = Activity(
            stage=stage,
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            entregavel=request.POST.get('entregavel', ''),
            assigned_to_id=assigned_to_id,
            delegated_by=request.user,
            activity_type=request.POST.get('activity_type', 'tarefa'),
            start_date=request.POST.get('start_date') or None,
            expected_date=request.POST.get('expected_date') or None,
            assigned_at=timezone.now() if assigned_to_id else None,
        )
        activity.save()

        # Criar histórico de criação
        ActivityHistory.objects.create(
            activity=activity,
            changed_by=request.user,
            change_type='criacao',
            change_details=f'Atividade criada por {request.user.get_full_name()}'
        )

        # Se foi atribuída, criar histórico específico de atribuição e notificar
        if assigned_to_id and activity.assigned_to:
            ActivityHistory.objects.create(
                activity=activity,
                changed_by=request.user,
                change_type='atribuicao',
                change_details=f'Atividade atribuída para {activity.assigned_to.get_full_name()} por {request.user.get_full_name()}'
            )
            notify_activity_assigned(activity, request.user)

        messages.success(request, 'Atividade criada com sucesso!')
        return redirect('prospecta:activities_list')

    context.update({
        'opportunities': opportunities,
        'users': User.objects.filter(profile__is_active=True).order_by('first_name', 'last_name'),
        'activity_type_choices': Activity.ACTIVITY_TYPE_CHOICES,
    })
    return render(request, 'prospecta/activities/form_standalone.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def activity_create(request, stage_pk):
    """Criar nova atividade em uma etapa"""
    stage = get_object_or_404(Stage, pk=stage_pk)
    context = get_user_context(request.user)

    if request.method == 'POST':
        assigned_to_id = request.POST.get('assigned_to') or None

        activity = Activity(
            stage=stage,
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            entregavel=request.POST.get('entregavel', ''),
            assigned_to_id=assigned_to_id,
            delegated_by=request.user,
            activity_type=request.POST.get('activity_type', 'tarefa'),
            start_date=request.POST.get('start_date') or None,
            expected_date=request.POST.get('expected_date') or None,
            assigned_at=timezone.now() if assigned_to_id else None,
        )
        activity.save()

        # Criar histórico de criação
        ActivityHistory.objects.create(
            activity=activity,
            changed_by=request.user,
            change_type='criacao',
            change_details=f'Atividade criada por {request.user.get_full_name()}'
        )

        # Se foi atribuída, criar histórico específico de atribuição e notificar
        if assigned_to_id and activity.assigned_to:
            ActivityHistory.objects.create(
                activity=activity,
                changed_by=request.user,
                change_type='atribuicao',
                change_details=f'Atividade atribuída para {activity.assigned_to.get_full_name()} por {request.user.get_full_name()}'
            )
            # Notificar o usuário atribuído
            notify_activity_assigned(activity, request.user)

        messages.success(request, 'Atividade criada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=stage.opportunity.pk)

    context.update({
        'stage': stage,
        'users': User.objects.filter(profile__is_active=True).order_by('first_name', 'last_name'),
        'activity_type_choices': Activity.ACTIVITY_TYPE_CHOICES,
    })
    return render(request, 'prospecta/activities/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def activity_update(request, pk):
    """Editar atividade"""
    activity = get_object_or_404(Activity, pk=pk)
    old_assigned_to = activity.assigned_to

    if request.method == 'POST':
        new_assigned_to_id = request.POST.get('assigned_to') or None

        activity.title = request.POST['title']
        activity.description = request.POST.get('description', '')
        activity.entregavel = request.POST.get('entregavel', '')
        activity.activity_type = request.POST.get(
            'activity_type', activity.activity_type)
        activity.start_date = request.POST.get('start_date') or None
        activity.expected_date = request.POST.get('expected_date') or None
        activity.status = request.POST.get('status', activity.status)

        # Verificar se houve mudança de atribuição
        old_assigned_to_id = old_assigned_to.id if old_assigned_to else None
        new_assigned_to_id_int = int(
            new_assigned_to_id) if new_assigned_to_id else None

        if old_assigned_to_id != new_assigned_to_id_int:
            activity.assigned_to_id = new_assigned_to_id
            activity.assigned_at = timezone.now() if new_assigned_to_id else None

            # Buscar novo usuário
            new_assigned_to = None
            if new_assigned_to_id:
                try:
                    new_assigned_to = User.objects.get(id=new_assigned_to_id)
                except User.DoesNotExist:
                    pass

            # Criar histórico de reatribuição
            if old_assigned_to or new_assigned_to:
                old_name = old_assigned_to.get_full_name() if old_assigned_to else 'Ninguém'
                new_name = new_assigned_to.get_full_name() if new_assigned_to else 'Ninguém'

                ActivityHistory.objects.create(
                    activity=activity,
                    changed_by=request.user,
                    change_type='reatribuicao',
                    change_details=f'Atividade reatribuída de {old_name} para {new_name} por {request.user.get_full_name()}'
                )

                # Notificar sobre reatribuição
                notify_activity_reassigned(
                    activity, old_assigned_to, new_assigned_to, request.user)
        else:
            activity.assigned_to_id = new_assigned_to_id

        activity.save()

        ActivityHistory.objects.create(
            activity=activity,
            changed_by=request.user,
            change_type='atualizacao',
            change_details=f'Atividade atualizada por {request.user.get_full_name()}'
        )

        messages.success(request, 'Atividade atualizada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=activity.stage.opportunity.pk)

    context = get_user_context(request.user)
    context.update({
        'activity': activity,
        'users': User.objects.filter(profile__is_active=True).order_by('first_name', 'last_name'),
        'status_choices': Activity.STATUS_CHOICES,
        'activity_type_choices': Activity.ACTIVITY_TYPE_CHOICES,
    })
    return render(request, 'prospecta/activities/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def activity_delete(request, pk):
    """Deletar atividade"""
    activity = get_object_or_404(Activity, pk=pk)
    opportunity_pk = activity.stage.opportunity.pk

    if request.method == 'POST':
        activity.delete()
        messages.success(request, 'Atividade deletada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=opportunity_pk)

    context = get_user_context(request.user)
    context['activity'] = activity
    return render(request, 'prospecta/activities/confirm_delete.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def activity_move(request, pk):
    """
    Move uma atividade de uma etapa para outra.
    Endpoint AJAX para drag and drop.
    """
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)
    
    activity = get_object_or_404(Activity, pk=pk)
    old_stage = activity.stage
    
    # Obter a nova etapa do POST
    import json
    try:
        data = json.loads(request.body)
        new_stage_id = data.get('stage_id')
    except json.JSONDecodeError:
        new_stage_id = request.POST.get('stage_id')
    
    if not new_stage_id:
        return JsonResponse({'success': False, 'error': 'ID da etapa não fornecido'}, status=400)
    
    try:
        new_stage = Stage.objects.get(pk=new_stage_id)
    except Stage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Etapa não encontrada'}, status=404)
    
    # Verificar se a nova etapa pertence à mesma oportunidade
    if old_stage.opportunity != new_stage.opportunity:
        return JsonResponse({
            'success': False, 
            'error': 'Não é possível mover atividade para etapa de outra oportunidade'
        }, status=400)
    
    # Se a etapa é a mesma, não fazer nada
    if old_stage.pk == new_stage.pk:
        return JsonResponse({'success': True, 'message': 'Atividade já está nesta etapa'})
    
    # Mover a atividade
    activity.stage = new_stage
    activity.save()
    
    # Registrar no histórico
    ActivityHistory.objects.create(
        activity=activity,
        changed_by=request.user,
        change_type='movimentacao',
        change_details=f'Atividade movida de "{old_stage.name}" para "{new_stage.name}" por {request.user.get_full_name()}'
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Atividade movida para {new_stage.name}',
        'old_stage': str(old_stage.pk),
        'new_stage': str(new_stage.pk),
        'activity_title': activity.title
    })


# ============================================================================
# FLUXO DE SUBMISSÃO E VERIFICAÇÃO DE ATIVIDADES
# ============================================================================

@login_required(login_url='account_login')
def activity_submit_completion(request, pk):
    """
    Submeter atividade para verificação.
    O responsável deve adicionar notas de conclusão e selecionar um verificador.
    """
    activity = get_object_or_404(Activity, pk=pk)

    # Verificar se o usuário é o responsável pela atividade
    if activity.assigned_to != request.user:
        messages.error(
            request, 'Apenas o responsável pode submeter a atividade para verificação.')
        return redirect('prospecta:opportunity_detail', pk=activity.stage.opportunity.pk)

    # Verificar se a atividade pode ser submetida
    if not activity.can_be_submitted_for_verification():
        messages.error(
            request, 'Esta atividade não pode ser submetida para verificação no momento.')
        return redirect('prospecta:opportunity_detail', pk=activity.stage.opportunity.pk)

    context = get_user_context(request.user)

    if request.method == 'POST':
        completion_notes = request.POST.get('completion_notes', '').strip()
        verifier_id = request.POST.get('verifier')

        # Validar campos obrigatórios
        if not completion_notes:
            messages.error(request, 'As notas de conclusão são obrigatórias.')
            context.update({
                'activity': activity,
                'users': User.objects.filter(profile__is_active=True).exclude(id=request.user.id).order_by('first_name', 'last_name'),
            })
            return render(request, 'prospecta/activities/submit_completion.html', context)

        if not verifier_id:
            messages.error(request, 'Você deve selecionar um verificador.')
            context.update({
                'activity': activity,
                'users': User.objects.filter(profile__is_active=True).exclude(id=request.user.id).order_by('first_name', 'last_name'),
            })
            return render(request, 'prospecta/activities/submit_completion.html', context)

        try:
            verifier = User.objects.get(id=verifier_id)
        except User.DoesNotExist:
            messages.error(request, 'Verificador não encontrado.')
            return redirect('prospecta:opportunity_detail', pk=activity.stage.opportunity.pk)

        # Atualizar atividade
        activity.completion_notes = completion_notes
        activity.verifier = verifier
        activity.previous_assigned_to = request.user
        activity.assigned_to = verifier  # Transferir responsabilidade para o verificador
        activity.submission_date = timezone.now()
        activity.status = 'aguardando_verificacao'
        activity.approval_status = 'submetida'
        activity.save()

        # Criar histórico
        ActivityHistory.objects.create(
            activity=activity,
            changed_by=request.user,
            change_type='submissao',
            change_details=f'Atividade submetida para verificação de {verifier.get_full_name()} por {request.user.get_full_name()}'
        )

        # Criar comentário do sistema
        ActivityComment.objects.create(
            activity=activity,
            author=request.user,
            content=f"Atividade submetida para verificação.\n\n**Notas de conclusão:**\n{completion_notes}",
            is_system_message=True,
        )

        # Notificar o verificador
        notify_activity_submitted_for_verification(activity, request.user)

        messages.success(
            request, f'Atividade submetida para verificação de {verifier.get_full_name()}!')
        return redirect('prospecta:opportunity_detail', pk=activity.stage.opportunity.pk)

    # GET - exibir formulário
    # Obter usuários que podem verificar (gerentes e admins, exceto o próprio usuário)
    verifiers = User.objects.filter(
        profile__is_active=True,
        profile__role__in=['admin', 'gerente']
    ).exclude(id=request.user.id)

    # Sugerir quem delegou como verificador padrão
    suggested_verifier = activity.delegated_by if activity.delegated_by and activity.delegated_by != request.user else None

    context.update({
        'activity': activity,
        'users': verifiers,
        'suggested_verifier': suggested_verifier,
    })
    return render(request, 'prospecta/activities/submit_completion.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def activity_verify(request, pk):
    """
    Verificar/aprovar/reprovar uma atividade submetida.
    Apenas o verificador designado ou admins podem fazer isso.
    """
    activity = get_object_or_404(Activity, pk=pk)

    # Verificar permissão
    is_admin = request.user.profile.is_admin() if hasattr(
        request.user, 'profile') else False
    if activity.verifier != request.user and not is_admin:
        messages.error(
            request, 'Você não tem permissão para verificar esta atividade.')
        return redirect('prospecta:opportunity_detail', pk=activity.stage.opportunity.pk)

    # Verificar se a atividade está aguardando verificação
    if not activity.can_be_verified():
        messages.error(
            request, 'Esta atividade não está aguardando verificação.')
        return redirect('prospecta:opportunity_detail', pk=activity.stage.opportunity.pk)

    context = get_user_context(request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'aprovar':
            # Aprovar a atividade
            activity.approved = True
            activity.approval_date = timezone.now()
            activity.approved_by = request.user
            activity.status = 'concluida'
            activity.approval_status = 'aprovada'
            activity.end_date = timezone.now().date()
            activity.save()

            # Criar histórico
            ActivityHistory.objects.create(
                activity=activity,
                changed_by=request.user,
                change_type='aprovacao',
                change_details=f'Atividade aprovada por {request.user.get_full_name()}'
            )

            # Criar comentário do sistema
            ActivityComment.objects.create(
                activity=activity,
                author=request.user,
                content="Atividade aprovada.",
                is_system_message=True,
            )

            # Notificar o responsável anterior
            notify_activity_approved(activity, request.user)

            messages.success(request, 'Atividade aprovada com sucesso!')

        elif action == 'reprovar':
            rejection_reason = request.POST.get('rejection_reason', '').strip()

            if not rejection_reason:
                messages.error(
                    request, 'O motivo da reprovação é obrigatório.')
                context.update({
                    'activity': activity,
                    'comments': activity.comments.all().order_by('created_at'),
                })
                return render(request, 'prospecta/activities/verify.html', context)

            # Guardar o responsável anterior para notificação
            original_assignee = activity.previous_assigned_to

            # Reprovar e devolver para o responsável anterior
            activity.rejection_reason = rejection_reason
            activity.assigned_to = original_assignee
            activity.previous_assigned_to = request.user  # Guardar quem reprovou
            activity.status = 'em_andamento'
            activity.approval_status = 'reprovada'
            activity.approved = False
            activity.approval_date = None
            activity.approved_by = None
            activity.submission_date = None
            activity.assigned_at = timezone.now()
            activity.save()

            # Criar histórico
            ActivityHistory.objects.create(
                activity=activity,
                changed_by=request.user,
                change_type='reprovacao',
                change_details=f'Atividade reprovada por {request.user.get_full_name()}. Motivo: {rejection_reason}'
            )

            # Criar comentário do sistema
            ActivityComment.objects.create(
                activity=activity,
                author=request.user,
                content=f"Atividade reprovada.\n\n**Motivo:**\n{rejection_reason}",
                is_system_message=True,
            )

            # Notificar o responsável original
            if original_assignee:
                activity.previous_assigned_to = original_assignee  # Restaurar para notificação
                notify_activity_rejected(
                    activity, request.user, rejection_reason)

            messages.warning(
                request, 'Atividade reprovada e devolvida para correções.')

        return redirect('prospecta:opportunity_detail', pk=activity.stage.opportunity.pk)

    # GET - exibir formulário de verificação
    context.update({
        'activity': activity,
        'comments': activity.comments.all().order_by('created_at'),
    })
    return render(request, 'prospecta/activities/verify.html', context)


@login_required(login_url='account_login')
@require_http_methods(["POST"])
def activity_add_comment(request, pk):
    """Adicionar comentário a uma atividade"""
    activity = get_object_or_404(Activity, pk=pk)

    # Verificar se o usuário tem permissão (responsável, verificador ou delegador)
    allowed = (
        activity.assigned_to == request.user or
        activity.verifier == request.user or
        activity.delegated_by == request.user or
        request.user.profile.is_manager()
    )

    if not allowed:
        messages.error(
            request, 'Você não tem permissão para comentar nesta atividade.')
        return redirect('prospecta:opportunity_detail', pk=activity.stage.opportunity.pk)

    content = request.POST.get('content', '').strip()

    if not content:
        messages.error(request, 'O comentário não pode estar vazio.')
        return redirect('prospecta:opportunity_detail', pk=activity.stage.opportunity.pk)

    # Criar comentário
    comment = ActivityComment.objects.create(
        activity=activity,
        author=request.user,
        content=content,
    )

    # Notificar outros envolvidos
    notify_activity_comment(comment)

    messages.success(request, 'Comentário adicionado!')

    # Redirecionar de volta para a página anterior
    referer = request.META.get('HTTP_REFERER', '')
    if 'verificar' in referer:
        return redirect('prospecta:activity_verify', pk=activity.pk)
    elif 'atividades' in referer and str(activity.pk) in referer:
        return redirect('prospecta:activity_detail', pk=activity.pk)
    return redirect('prospecta:opportunity_detail', pk=activity.stage.opportunity.pk)


# ============================================================================
# NOTIFICAÇÕES
# ============================================================================

@login_required(login_url='account_login')
def notifications_list(request):
    """Lista de notificações do usuário"""
    context = get_user_context(request.user)

    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    # Filtro por status
    filter_status = request.GET.get('status', 'all')
    if filter_status == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_status == 'read':
        notifications = notifications.filter(is_read=True)

    context.update({
        'notifications': notifications[:50],
        'unread_count': notifications.filter(is_read=False).count(),
        'filter_status': filter_status,
    })
    return render(request, 'prospecta/notifications/list.html', context)


@login_required(login_url='account_login')
def notification_mark_read(request, pk):
    """Marcar uma notificação como lida e redirecionar"""
    notification = get_object_or_404(
        Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()

    # Se há URL de ação, redirecionar
    if notification.action_url:
        return redirect(notification.action_url)

    return redirect('prospecta:notifications_list')


@login_required(login_url='account_login')
@require_http_methods(["POST"])
def notifications_mark_all_read(request):
    """Marcar todas as notificações como lidas"""
    mark_all_as_read(request.user)
    messages.success(
        request, 'Todas as notificações foram marcadas como lidas.')
    return redirect('prospecta:notifications_list')


@login_required(login_url='account_login')
def notifications_dropdown(request):
    """HTMX endpoint para dropdown de notificações"""
    notifications = get_recent_notifications(request.user, limit=5)
    unread_count = get_unread_notifications_count(request.user)

    return render(request, 'prospecta/components/notifications_dropdown.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required(login_url='account_login')
def notifications_count(request):
    """API endpoint para contagem de notificações não lidas - retorna ícone do sino"""
    count = get_unread_notifications_count(request.user)
    if count > 0:
        return HttpResponse('<i class="fas fa-bell text-xl text-red-500 animate-wiggle"></i>')
    else:
        return HttpResponse('<i class="fas fa-bell text-xl"></i>')


# ============================================================================
# CONTACTS (Contatos de Empresa)
# ============================================================================

@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def contact_create(request, client_pk):
    """Criar novo contato em uma empresa"""
    client = get_object_or_404(Client, pk=client_pk)
    context = get_user_context(request.user)

    if request.method == 'POST':
        contact = Contact(
            client=client,
            name=request.POST['name'],
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            position=request.POST.get('position', ''),
            notes=request.POST.get('notes', ''),
        )
        contact.save()
        messages.success(request, 'Contato criado com sucesso!')
        return redirect('prospecta:client_detail', pk=client.pk)

    context['client'] = client
    return render(request, 'prospecta/contacts/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def contact_update(request, pk):
    """Editar contato"""
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == 'POST':
        contact.name = request.POST['name']
        contact.email = request.POST.get('email', '')
        contact.phone = request.POST.get('phone', '')
        contact.position = request.POST.get('position', '')
        contact.notes = request.POST.get('notes', '')
        contact.save()

        messages.success(request, 'Contato atualizado com sucesso!')
        return redirect('prospecta:client_detail', pk=contact.client.pk)

    context = get_user_context(request.user)
    context['contact'] = contact
    return render(request, 'prospecta/contacts/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def contact_delete(request, pk):
    """Deletar contato"""
    contact = get_object_or_404(Contact, pk=pk)
    client_pk = contact.client.pk

    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Contato deletado com sucesso!')
        return redirect('prospecta:client_detail', pk=client_pk)

    context = get_user_context(request.user)
    context['contact'] = contact
    return render(request, 'prospecta/contacts/confirm_delete.html', context)


# ============================================================================
# SALES MODELS (Modelos de Venda)
# ============================================================================

@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def sales_model_list(request):
    """Lista de modelos de venda"""
    context = get_user_context(request.user)
    models = SalesModel.objects.all().order_by('name')

    search = request.GET.get('search')
    if search:
        models = models.filter(Q(name__icontains=search)
                               | Q(description__icontains=search))

    context['sales_models'] = models
    return render(request, 'prospecta/sales_models/list.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def sales_model_create(request):
    """Criar novo modelo de venda"""
    context = get_user_context(request.user)

    if request.method == 'POST':
        model = SalesModel(
            name=request.POST['name'],
            description=request.POST.get('description', ''),
        )
        model.save()
        messages.success(request, 'Modelo de venda criado com sucesso!')
        return redirect('prospecta:sales_model_list')

    return render(request, 'prospecta/sales_models/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def sales_model_update(request, pk):
    """Editar modelo de venda"""
    model = get_object_or_404(SalesModel, pk=pk)

    if request.method == 'POST':
        model.name = request.POST['name']
        model.description = request.POST.get('description', '')
        model.save()

        messages.success(request, 'Modelo de venda atualizado com sucesso!')
        return redirect('prospecta:sales_model_list')

    context = get_user_context(request.user)
    context['sales_model'] = model
    return render(request, 'prospecta/sales_models/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def sales_model_delete(request, pk):
    """Deletar modelo de venda"""
    model = get_object_or_404(SalesModel, pk=pk)

    if request.method == 'POST':
        model.delete()
        messages.success(request, 'Modelo de venda deletado com sucesso!')
        return redirect('prospecta:sales_model_list')

    context = get_user_context(request.user)
    context['sales_model'] = model
    return render(request, 'prospecta/sales_models/confirm_delete.html', context)


# ============================================================================
# LIST VIEWS (Páginas de Listagem)
# ============================================================================

@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def stages_list(request):
    """Lista de todas as etapas"""
    context = get_user_context(request.user)

    if request.user.profile.is_admin() or request.user.profile.is_manager():
        stages = Stage.objects.all().order_by('opportunity', 'order')
    else:
        stages = Stage.objects.filter(
            opportunity__responsible_user=request.user
        ).order_by('opportunity', 'order')

    context['stages'] = stages
    return render(request, 'prospecta/stages/list.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def contacts_list(request):
    """Lista de todos os contatos"""
    context = get_user_context(request.user)

    if request.user.profile.is_admin() or request.user.profile.is_manager():
        contacts = Contact.objects.all().order_by('client', 'name')
    else:
        contacts = Contact.objects.filter(
            client__created_by=request.user
        ).order_by('client', 'name')

    context['contacts'] = contacts
    return render(request, 'prospecta/contacts/list.html', context)


# ============================================================================
# Opportunity Participants Management
# ============================================================================

@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def add_opportunity_participant(request, pk):
    """Adicionar participante à oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)

    # Verificar permissão
    if not (request.user == opportunity.responsible_user or
            request.user == opportunity.created_by or
            request.user.profile.is_manager()):
        messages.error(
            request, 'Você não tem permissão para adicionar participantes nesta oportunidade.')
        return redirect('prospecta:opportunity_detail', pk=pk)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            participant, created = OpportunityParticipant.objects.get_or_create(
                opportunity=opportunity,
                user=user,
                defaults={'added_by': request.user}
            )
            if created:
                messages.success(
                    request, f'{user.get_full_name()} foi adicionado como participante.')
            else:
                messages.info(
                    request, f'{user.get_full_name()} já era participante.')
        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')

        return redirect('prospecta:opportunity_detail', pk=pk)

    # Listar usuários disponíveis (não serem já participantes)
    current_participants = opportunity.participants.values_list(
        'user_id', flat=True)
    available_users = User.objects.filter(
        profile__is_active=True
    ).exclude(id__in=current_participants)

    context = {
        'opportunity': opportunity,
        'available_users': available_users,
    }

    return render(request, 'prospecta/opportunities/add_participant.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
@require_http_methods(["POST"])
def remove_opportunity_participant(request, pk, participant_id):
    """Remover participante da oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    participant = get_object_or_404(
        OpportunityParticipant, id=participant_id, opportunity=opportunity)

    # Verificar permissão
    if not (request.user == opportunity.responsible_user or
            request.user == opportunity.created_by or
            request.user.profile.is_manager()):
        messages.error(
            request, 'Você não tem permissão para remover participantes.')
        return redirect('prospecta:opportunity_detail', pk=pk)

    user_name = participant.user.get_full_name()
    participant.delete()
    messages.success(request, f'{user_name} foi removido como participante.')

    return redirect('prospecta:opportunity_detail', pk=pk)


@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def toggle_participant_notifications(request, pk, participant_id):
    """Alternar notificações de um participante"""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    participant = get_object_or_404(
        OpportunityParticipant, id=participant_id, opportunity=opportunity)

    # Verificar permissão
    if not (request.user == opportunity.responsible_user or
            request.user == opportunity.created_by or
            request.user.profile.is_manager()):
        messages.error(request, 'Você não tem permissão.')
        return redirect('prospecta:opportunity_detail', pk=pk)

    participant.notify_on_update = not participant.notify_on_update
    participant.save()

    status = 'ativadas' if participant.notify_on_update else 'desativadas'
    messages.success(
        request, f'Notificações {status} para {participant.user.get_full_name()}.')

    return redirect('prospecta:opportunity_detail', pk=pk)


# ============================================================================
# Global Search
# ============================================================================

@login_required(login_url='account_login')
@require_http_methods(["POST"])
def search_global(request):
    """Busca global de oportunidades, empresas, atividades"""
    query = request.POST.get('q', '').strip()

    if not query or len(query) < 2:
        return HttpResponse('')

    from .utils import get_user_context
    context = get_user_context(request.user)

    # Inicializar resultados
    results = {
        'opportunities': [],
        'clients': [],
        'activities': [],
        'contacts': [],
    }

    # Buscar oportunidades
    if context['is_manager'] or context['is_analista']:
        opportunities = Opportunity.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:5]
        results['opportunities'] = [
            {
                'title': o.title,
                'client': o.client.name,
                'url': f"/oportunidades/{o.pk}/",
                'status': o.status
            }
            for o in opportunities
        ]

    # Buscar clientes
    if context['is_manager']:
        clients = Client.objects.filter(
            Q(name__icontains=query) | Q(cnpj__icontains=query)
        )[:5]
        results['clients'] = [
            {
                'name': c.name,
                'cnpj': c.cnpj,
                'url': f"/clientes/{c.pk}/",
            }
            for c in clients
        ]

    # Buscar atividades
    if not context['is_visitor']:
        activities = Activity.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:5]
        results['activities'] = [
            {
                'title': a.title,
                'stage': a.stage.name,
                'url': f"/atividades/{a.pk}/editar/",
            }
            for a in activities
        ]

    # Buscar contatos
    if context['is_manager']:
        contacts = Contact.objects.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        )[:5]
        results['contacts'] = [
            {
                'name': c.name,
                'email': c.email,
                'client': c.client.name,
                'url': f"/contatos/{c.pk}/editar/",
            }
            for c in contacts
        ]

    # Renderizar template com resultados
    return render(request, 'prospecta/components/search_results.html', {
        'results': results,
        'query': query
    })
