from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from django.utils.decorators import method_decorator
from django.contrib import messages

from .models import (
    UserProfile, Client, Contact, SalesModel, Opportunity, 
    Stage, Activity, OpportunityHistory, StageHistory, ActivityHistory
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


def get_user_context(user):
    """Retorna contexto com dados do usuário e suas permissões"""
    context = {
        'user': user,
        'is_admin': False,
        'is_manager': False,
        'is_seller': False,
    }
    
    if user.is_authenticated:
        try:
            profile = user.profile
            context['profile'] = profile
            context['is_admin'] = profile.is_admin()
            context['is_manager'] = profile.is_manager()
            context['is_seller'] = profile.is_seller()
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
    """Dashboard principal do sistema"""
    context = get_user_context(request.user)
    
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Se o usuário não tem perfil, criar um padrão
        profile = UserProfile.objects.create(user=request.user)
    
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
        opportunities = Opportunity.objects.filter(responsible_user=request.user)
        activities = Activity.objects.filter(assigned_to=request.user)
        users = None
    
    # Cálculos de dashboard
    context.update({
        'opportunities_count': opportunities.count(),
        'activities_count': activities.count(),
        'recent_opportunities': opportunities.order_by('-created_at')[:5],
        'pending_activities': activities.filter(status='pendente').count(),
        'total_pipeline': opportunities.aggregate(Sum('value_brl'))['value_brl__sum'] or 0,
        'won_opportunities': opportunities.filter(status='ganha').count(),
    })
    
    if profile.is_admin() and users:
        context['users_count'] = users.count()
    
    return render(request, 'prospecta/dashboard.html', context)


@login_required(login_url='account_login')
def profile_view(request):
    """Página de perfil do usuário"""
    context = get_user_context(request.user)
    
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
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
@role_required('admin', 'gerente', 'vendedor')
def opportunities_list(request):
    """Lista de oportunidades com filtros"""
    context = get_user_context(request.user)
    
    # Filtros baseados no role
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if profile.is_admin():
        opportunities = Opportunity.objects.all()
    elif profile.is_manager():
        opportunities = Opportunity.objects.filter(
            Q(created_by=request.user) | Q(responsible_user=request.user)
        )
    else:
        opportunities = Opportunity.objects.filter(responsible_user=request.user)
    
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
@role_required('admin', 'gerente', 'vendedor')
def opportunity_create(request):
    """Criar nova oportunidade"""
    context = get_user_context(request.user)
    
    if request.method == 'POST':
        opportunity = Opportunity(
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            client_id=request.POST['client'],
            created_by=request.user,
            responsible_user_id=request.POST.get('responsible_user', request.user.id),
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
    """Detalhes de uma oportunidade"""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    
    # Verificar permissão
    try:
        profile = request.user.profile
        if not profile.is_admin() and opportunity.responsible_user != request.user and opportunity.created_by != request.user:
            return redirect('prospecta:opportunities_list')
    except UserProfile.DoesNotExist:
        return redirect('account_login')
    
    context = get_user_context(request.user)
    context.update({
        'opportunity': opportunity,
        'stages': opportunity.stages.all().order_by('order'),
        'history': opportunity.history.all()[:10],
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
        opportunity.expected_delivery_date = request.POST.get('expected_delivery_date')
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
        opportunities = Opportunity.objects.filter(responsible_user=request.user)
    
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
@role_required('admin', 'gerente', 'analista')
def clients_list(request):
    """Lista de clientes"""
    context = get_user_context(request.user)
    clients = Client.objects.all()
    
    search = request.GET.get('search')
    if search:
        clients = clients.filter(
            Q(name__icontains=search) | Q(cnpj__icontains=search) | Q(email__icontains=search)
        )
    
    context['clients'] = clients.order_by('name')
    return render(request, 'prospecta/clients/list.html', context)


@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def client_create(request):
    """Criar novo cliente"""
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
        messages.success(request, 'Cliente criado com sucesso!')
        return redirect('prospecta:client_detail', pk=client.pk)
    
    return render(request, 'prospecta/clients/form.html', context)


@login_required(login_url='account_login')
def client_detail(request, pk):
    """Detalhes do cliente"""
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
    """Editar cliente"""
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        client.name = request.POST['name']
        client.cnpj = request.POST['cnpj']
        client.address = request.POST.get('address', '')
        client.phone = request.POST.get('phone', '')
        client.email = request.POST.get('email', '')
        client.save()
        messages.success(request, 'Cliente atualizado com sucesso!')
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
    
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
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
def reports(request):
    """Página de relatórios"""
    context = get_user_context(request.user)
    
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    # Dados para relatórios
    if profile.is_admin():
        opportunities = Opportunity.objects.all()
    else:
        opportunities = Opportunity.objects.filter(responsible_user=request.user)
    
    # Estatísticas
    context.update({
        'total_opportunities': opportunities.count(),
        'won_opportunities': opportunities.filter(status='ganha').count(),
        'lost_opportunities': opportunities.filter(status='perdida').count(),
        'open_opportunities': opportunities.filter(status='aberta').count(),
        'total_value': opportunities.aggregate(Sum('value_brl'))['value_brl__sum'] or 0,
        'won_value': opportunities.filter(status='ganha').aggregate(Sum('value_brl'))['value_brl__sum'] or 0,
    })
    
    return render(request, 'prospecta/reports.html', context)


# ============================================================================
# Google OAuth Views
# ============================================================================

@require_http_methods(['GET'])
def google_oauth_login(request):
    """Redireciona para o Google OAuth consent screen"""
    from allauth.socialaccount.models import SocialApp
    from django.contrib.sites.models import Site
    from urllib.parse import urlencode
    
    try:
        # Pega a SocialApp do Google
        google_app = SocialApp.objects.get(provider='google')
        current_site = Site.objects.get_current()
        
        # Parâmetros para o Google OAuth
        oauth_params = {
            'client_id': google_app.client_id,
            'redirect_uri': f'http://{current_site.domain}/accounts/google/login/callback/',
            'response_type': 'code',
            'scope': 'openid email profile',
            'access_type': 'online',
        }
        
        google_oauth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(oauth_params)
        return redirect(google_oauth_url)
    except SocialApp.DoesNotExist:
        messages.error(request, 'Google OAuth não está configurado.')
        return redirect('account_login')
