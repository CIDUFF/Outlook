from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib import messages

from .models import (
    UserProfile, Client, Contact, SalesModel, Opportunity,
    Stage, Activity, OpportunityHistory, StageHistory, ActivityHistory,
    OpportunityParticipant
)


# ============================================================================
# Decorators and helpers
# ============================================================================

def role_required(*roles):
    """Decorator para verificar role do usuário"""
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
    """Decorator para verificar permissão de escrita (visitantes não podem)"""
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


def get_user_context(user):
    """Retorna contexto com dados do usuário e suas permissões"""
    context = {
        'user': user,
        'is_admin': False,
        'is_manager': False,
        'is_analyst': False,
        'is_visitor': False,
        'can_write': False,
    }

    if user.is_authenticated:
        try:
            profile = user.profile
            context['profile'] = profile
            context['is_admin'] = profile.is_admin()
            context['is_manager'] = profile.is_manager()
            context['is_analyst'] = profile.is_analyst()
            context['is_visitor'] = profile.is_visitor()
            context['can_write'] = profile.can_write()
        except UserProfile.DoesNotExist:
            pass

    return context


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
            'open_opportunities': Opportunity.objects.filter(status='aberta').count(),
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
    if profile.is_admin():
        # Administrador vê tudo
        opportunities = Opportunity.objects.all()
        activities = Activity.objects.all()
        users = User.objects.all()
    elif profile.is_manager():
        # Gerente vê suas oportunidades e atividades
        opportunities = Opportunity.objects.filter(
            Q(created_by=request.user) | Q(responsible_user=request.user)
        )
        activities = Activity.objects.filter(
            Q(stage__opportunity__in=opportunities) |
            Q(assigned_to=request.user)
        )
        users = None
    else:
        # Vendedor vê apenas suas oportunidades e atividades
        opportunities = Opportunity.objects.filter(
            responsible_user=request.user)
        activities = Activity.objects.filter(assigned_to=request.user)
        users = None

    # KPIs - Oportunidades
    total_opportunities = opportunities.count()
    open_opportunities = opportunities.filter(status='aberta').count()
    in_progress_opportunities = opportunities.filter(
        status='em_andamento').count()
    won_opportunities = opportunities.filter(status='ganha').count()
    lost_opportunities = opportunities.filter(status='perdida').count()

    # Valores
    total_pipeline = opportunities.aggregate(
        Sum('value_brl'))['value_brl__sum'] or 0
    won_value = opportunities.filter(status='ganha').aggregate(
        Sum('value_brl'))['value_brl__sum'] or 0
    in_progress_value = opportunities.filter(status='em_andamento').aggregate(
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
        'aberta': open_opportunities,
        'em_andamento': in_progress_opportunities,
        'ganha': won_opportunities,
        'perdida': lost_opportunities,
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
        'open_opportunities': open_opportunities,
        'in_progress_opportunities': in_progress_opportunities,
        'won_opportunities': won_opportunities,
        'lost_opportunities': lost_opportunities,
        'opportunities_count': total_opportunities,

        # Valores
        'total_pipeline': total_pipeline,
        'won_value': won_value,
        'in_progress_value': in_progress_value,
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

    # Filtros baseados no role
    if profile.is_admin():
        opportunities = Opportunity.objects.all()
    elif profile.is_manager():
        opportunities = Opportunity.objects.filter(
            Q(created_by=request.user) | Q(responsible_user=request.user)
        )
    else:
        opportunities = Opportunity.objects.filter(
            responsible_user=request.user)

    # Aplicar filtros
    status = request.GET.get('status')
    if status:
        opportunities = opportunities.filter(status=status)

    client_id = request.GET.get('client')
    if client_id:
        opportunities = opportunities.filter(client_id=client_id)

    # Ordenação
    sort = request.GET.get('sort', '-created_at')
    opportunities = opportunities.order_by(sort)

    context.update({
        'opportunities': opportunities,
        'clients': Client.objects.all(),
        'status_choices': Opportunity.STATUS_CHOICES,
    })

    return render(request, 'prospecta/opportunities/list.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente', 'analista')
def opportunity_create(request):
    """Criar nova oportunidade"""
    context = get_user_context(request.user)

    if request.method == 'POST':
        opportunity = Opportunity(
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            client_id=request.POST['client'],
            created_by=request.user,
            responsible_user_id=request.POST.get(
                'responsible_user', request.user.id),
            sales_model_id=request.POST.get('sales_model'),
            value_brl=request.POST.get('value_brl'),
            expected_delivery_date=request.POST.get('expected_delivery_date'),
        )
        opportunity.save()

        # Criar histórico
        OpportunityHistory.objects.create(
            opportunity=opportunity,
            changed_by=request.user,
            change_type='criacao',
            change_details=f'Oportunidade criada por {request.user.get_full_name()}'
        )

        messages.success(request, 'Oportunidade criada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=opportunity.pk)

    context.update({
        'clients': Client.objects.all(),
        'sales_models': SalesModel.objects.all(),
        'users': User.objects.filter(profile__is_active=True),
    })

    return render(request, 'prospecta/opportunities/form.html', context)


@login_required(login_url='account_login')
def opportunity_detail(request, pk):
    """Detalhes da oportunidade"""
    """Detalhes de uma oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)

    # Verificar permissão
    try:
        profile = request.user.profile
        if not profile.is_admin() and opportunity.responsible_user != request.user and opportunity.created_by != request.user:
            return redirect('prospecta:opportunities_list')
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

    context = get_user_context(request.user)
    context.update({
        'opportunity': opportunity,
        'stages': opportunity.stages.all().order_by('order'),
        'history': opportunity.history.all()[:10],
        'available_users': available_users,
        'opportunity_activity_count': opportunity_activity_count,
    })

    return render(request, 'prospecta/opportunities/detail.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def opportunity_update(request, pk):
    """Editar oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)

    if request.method == 'POST':
        opportunity.title = request.POST['title']
        opportunity.description = request.POST.get('description', '')
        opportunity.client_id = request.POST['client']
        opportunity.responsible_user_id = request.POST['responsible_user']
        opportunity.sales_model_id = request.POST.get('sales_model')
        opportunity.value_brl = request.POST.get('value_brl')
        opportunity.expected_delivery_date = request.POST.get(
            'expected_delivery_date')
        opportunity.status = request.POST.get('status', opportunity.status)
        opportunity.save()

        OpportunityHistory.objects.create(
            opportunity=opportunity,
            changed_by=request.user,
            change_type='atualizacao',
            change_details=f'Oportunidade atualizada por {request.user.get_full_name()}'
        )

        messages.success(request, 'Oportunidade atualizada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=opportunity.pk)

    context = get_user_context(request.user)
    context.update({
        'opportunity': opportunity,
        'clients': Client.objects.all(),
        'sales_models': SalesModel.objects.all(),
        'users': User.objects.filter(profile__is_active=True),
        'status_choices': Opportunity.STATUS_CHOICES,
    })

    return render(request, 'prospecta/opportunities/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def opportunity_delete(request, pk):
    """Deletar oportunidade"""
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
    except UserProfile.DoesNotExist:
        return HttpResponse('')

    if profile.is_admin():
        opportunities = Opportunity.objects.all()
    elif profile.is_manager():
        opportunities = Opportunity.objects.filter(
            Q(created_by=request.user) | Q(responsible_user=request.user)
        )
    else:
        opportunities = Opportunity.objects.filter(
            responsible_user=request.user)

    status = request.GET.get('status')
    if status:
        opportunities = opportunities.filter(status=status)

    return render(request, 'prospecta/components/opportunities_table.html', {
        'opportunities': opportunities
    })


@login_required(login_url='account_login')
@require_http_methods(['POST'])
def opportunity_status_update(request, pk):
    """HTMX endpoint para atualizar status da oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    new_status = request.POST.get('status')

    if new_status in dict(Opportunity.STATUS_CHOICES):
        opportunity.status = new_status
        opportunity.save()

        OpportunityHistory.objects.create(
            opportunity=opportunity,
            changed_by=request.user,
            change_type='atualizacao_status',
            change_details=f'Status alterado para {new_status} por {request.user.get_full_name()}'
        )

    return render(request, 'prospecta/components/opportunity_badge.html', {
        'opportunity': opportunity
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
            Q(name__icontains=search) | Q(
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
            cnpj=request.POST['cnpj'],
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
        client.cnpj = request.POST['cnpj']
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

    if profile.is_admin():
        activities = Activity.objects.all()
    elif profile.is_manager():
        activities = Activity.objects.filter(
            Q(assigned_to=request.user) | Q(delegated_by=request.user)
        )
    else:
        activities = Activity.objects.filter(assigned_to=request.user)

    status = request.GET.get('status')
    if status:
        activities = activities.filter(status=status)

    context.update({
        'activities': activities.order_by('-created_at'),
        'pending_count': activities.filter(status='pendente').count(),
        'status_choices': Activity.STATUS_CHOICES,
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

    # Dados para relatórios
    if profile.is_admin():
        opportunities = Opportunity.objects.all()
    else:
        opportunities = Opportunity.objects.filter(
            responsible_user=request.user)

    # Contar oportunidades por status
    total_opp = opportunities.count()
    won_opp = opportunities.filter(status='ganha').count()
    lost_opp = opportunities.filter(status='perdida').count()
    open_opp = opportunities.filter(status='aberta').count()

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
        stage = Stage(
            opportunity=opportunity,
            name=request.POST['name'],
            order=request.POST.get('order', 1),
            created_by=request.user,
        )
        stage.save()

        StageHistory.objects.create(
            stage=stage,
            changed_by=request.user,
            change_type='criacao',
            change_details=f'Etapa criada por {request.user.get_full_name()}'
        )

        messages.success(request, 'Etapa criada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=opportunity.pk)

    context['opportunity'] = opportunity
    return render(request, 'prospecta/stages/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def stage_update(request, pk):
    """Editar etapa"""
    stage = get_object_or_404(Stage, pk=pk)

    if request.method == 'POST':
        stage.name = request.POST['name']
        stage.order = request.POST.get('order', stage.order)
        stage.save()

        StageHistory.objects.create(
            stage=stage,
            changed_by=request.user,
            change_type='atualizacao',
            change_details=f'Etapa atualizada por {request.user.get_full_name()}'
        )

        messages.success(request, 'Etapa atualizada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=stage.opportunity.pk)

    context = get_user_context(request.user)
    context['stage'] = stage
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
@role_required('admin', 'gerente')
def activity_create(request, stage_pk):
    """Criar nova atividade em uma etapa"""
    stage = get_object_or_404(Stage, pk=stage_pk)
    context = get_user_context(request.user)

    if request.method == 'POST':
        activity = Activity(
            stage=stage,
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            assigned_to_id=request.POST.get('assigned_to') or None,
            delegated_by=request.user,
            start_date=request.POST.get('start_date') or None,
            expected_date=request.POST.get('expected_date') or None,
        )
        activity.save()

        ActivityHistory.objects.create(
            activity=activity,
            changed_by=request.user,
            change_type='criacao',
            change_details=f'Atividade criada por {request.user.get_full_name()}'
        )

        messages.success(request, 'Atividade criada com sucesso!')
        return redirect('prospecta:opportunity_detail', pk=stage.opportunity.pk)

    context.update({
        'stage': stage,
        'users': User.objects.filter(profile__is_active=True),
    })
    return render(request, 'prospecta/activities/form.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def activity_update(request, pk):
    """Editar atividade"""
    activity = get_object_or_404(Activity, pk=pk)

    if request.method == 'POST':
        activity.title = request.POST['title']
        activity.description = request.POST.get('description', '')
        activity.assigned_to_id = request.POST.get('assigned_to') or None
        activity.start_date = request.POST.get('start_date') or None
        activity.expected_date = request.POST.get('expected_date') or None
        activity.status = request.POST.get('status', activity.status)
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
        'users': User.objects.filter(profile__is_active=True),
        'status_choices': Activity.STATUS_CHOICES,
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
