"""
Utilities for navigation, breadcrumbs, and common helper functions
"""
from functools import wraps
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages


def permission_required(*permission_names, redirect_url='prospecta:dashboard'):
    """
    Decorator para verificar permissões baseado na PermissionsMatrix.

    Uso:
        @permission_required('Criar Oportunidades')
        def create_opportunity(request):
            ...

        @permission_required('Editar Oportunidades', 'Excluir Oportunidades')
        def manage_opportunity(request):
            ...  # Precisa de qualquer uma das permissões

    Args:
        permission_names: Uma ou mais permissões necessárias (precisa de pelo menos uma)
        redirect_url: URL para redirecionar se não tiver permissão
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('account_login')

            try:
                profile = request.user.profile

                # Admins sempre têm permissão
                if profile.is_admin():
                    return view_func(request, *args, **kwargs)

                # Verifica se tem pelo menos uma das permissões
                for perm in permission_names:
                    if profile.has_permission(perm):
                        return view_func(request, *args, **kwargs)

                # Não tem permissão
                messages.error(
                    request,
                    f'Você não tem permissão para realizar esta ação. '
                    f'Permissão necessária: {" ou ".join(permission_names)}'
                )
                return redirect(redirect_url)

            except Exception:
                return redirect('account_login')

        return wrapper
    return decorator


def permissions_required_all(*permission_names, redirect_url='prospecta:dashboard'):
    """
    Decorator que exige TODAS as permissões listadas.

    Args:
        permission_names: Permissões necessárias (precisa de todas)
        redirect_url: URL para redirecionar se não tiver permissão
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('account_login')

            try:
                profile = request.user.profile

                # Admins sempre têm permissão
                if profile.is_admin():
                    return view_func(request, *args, **kwargs)

                # Verifica se tem todas as permissões
                for perm in permission_names:
                    if not profile.has_permission(perm):
                        messages.error(
                            request,
                            f'Você não tem permissão para realizar esta ação. '
                            f'Permissão necessária: {perm}'
                        )
                        return redirect(redirect_url)

                return view_func(request, *args, **kwargs)

            except Exception:
                return redirect('account_login')

        return wrapper
    return decorator


def get_breadcrumbs(view_name, **kwargs):
    """
    Generate breadcrumbs based on the current view

    Returns list of dicts with: label, url (optional), icon
    """
    breadcrumbs = [
        {'label': 'Home', 'url': reverse('prospecta:home'), 'icon': 'home'}
    ]

    # Oportunidades
    if 'opportunity' in view_name:
        breadcrumbs.append({
            'label': 'Oportunidades',
            'url': reverse('prospecta:opportunities_list'),
            'icon': 'handshake'
        })

        if 'detail' in view_name or 'update' in view_name:
            opportunity = kwargs.get('opportunity')
            if opportunity:
                breadcrumbs.append({
                    'label': opportunity.title,
                    'url': reverse('prospecta:opportunity_detail', args=[opportunity.pk]),
                    'icon': 'file-alt'
                })
        elif 'create' in view_name:
            breadcrumbs.append({
                'label': 'Criar Oportunidade',
                'url': None,
                'icon': 'plus'
            })

    # Clientes
    elif 'client' in view_name:
        breadcrumbs.append({
            'label': 'Clientes',
            'url': reverse('prospecta:clients_list'),
            'icon': 'building'
        })

        if 'detail' in view_name or 'update' in view_name:
            client = kwargs.get('client')
            if client:
                breadcrumbs.append({
                    'label': client.name,
                    'url': reverse('prospecta:client_detail', args=[client.pk]),
                    'icon': 'file-alt'
                })
        elif 'create' in view_name:
            breadcrumbs.append({
                'label': 'Novo Cliente',
                'url': None,
                'icon': 'plus'
            })

    # Contatos
    elif 'contact' in view_name:
        breadcrumbs.append({
            'label': 'Contatos',
            'url': reverse('prospecta:contacts_list'),
            'icon': 'users'
        })
        if 'create' in view_name or 'update' in view_name:
            breadcrumbs.append({
                'label': 'Editar Contato' if 'update' in view_name else 'Novo Contato',
                'url': None,
                'icon': 'plus'
            })

    # Atividades
    elif 'activity' in view_name:
        breadcrumbs.append({
            'label': 'Atividades',
            'url': reverse('prospecta:activities_list'),
            'icon': 'tasks'
        })
        if 'create' in view_name or 'update' in view_name:
            breadcrumbs.append({
                'label': 'Editar Atividade' if 'update' in view_name else 'Nova Atividade',
                'url': None,
                'icon': 'plus'
            })

    # Etapas
    elif 'stage' in view_name:
        breadcrumbs.append({
            'label': 'Etapas',
            'url': reverse('prospecta:stages_list'),
            'icon': 'bars'
        })
        if 'create' in view_name or 'update' in view_name:
            breadcrumbs.append({
                'label': 'Editar Etapa' if 'update' in view_name else 'Nova Etapa',
                'url': None,
                'icon': 'plus'
            })

    # Dashboard
    elif 'dashboard' in view_name:
        breadcrumbs = [
            {'label': 'Dashboard', 'url': None, 'icon': 'home'}
        ]

    return breadcrumbs


def get_user_context(user):
    """
    Get common context variables for all views.
    Includes permission checks, user role info, and matrix permissions.

    Esta é a função CANÔNICA - não use duplicatas em outros arquivos.
    """
    # Contexto padrão para usuários não autenticados
    default_context = {
        'user': user,
        'is_admin': False,
        'is_manager': False,
        'is_analyst': False,
        'is_analista': False,  # Alias para compatibilidade
        'is_visitor': True,
        'can_write': False,
        'user_role': 'Visitante',
        'permissions': {},
    }

    if not user or not user.is_authenticated:
        return default_context

    try:
        profile = user.profile
    except Exception:
        return default_context

    # Buscar permissões da matriz
    permissions = profile.get_all_permissions()

    return {
        'user': user,
        'profile': profile,
        'is_admin': profile.is_admin(),
        'is_manager': profile.is_manager(),
        'is_analyst': profile.is_analyst(),
        'is_analista': profile.role == 'analista',  # Alias para compatibilidade
        'is_visitor': profile.is_visitor(),
        'can_write': profile.can_write(),
        'user_role': profile.get_role_display(),
        'permissions': permissions,
        # Atalhos para permissões comuns (para uso fácil em templates)
        'can_create_opportunities': permissions.get('Criar Oportunidades', False),
        'can_edit_opportunities': permissions.get('Editar Oportunidades', False),
        'can_delete_opportunities': permissions.get('Excluir Oportunidades', False),
        'can_create_clients': permissions.get('Criar Clientes', False),
        'can_edit_clients': permissions.get('Editar Clientes', False),
        'can_delete_clients': permissions.get('Excluir Clientes', False),
        'can_create_activities': permissions.get('Criar Atividades', False),
        'can_edit_activities': permissions.get('Editar Atividades', False),
        'can_delete_activities': permissions.get('Excluir Atividades', False),
        'can_approve_activities': permissions.get('Aprovar Atividades', False),
        'can_manage_users': permissions.get('Gerenciar Usuários', False),
        'can_manage_permissions': permissions.get('Gerenciar Permissões', False),
        'can_view_reports': permissions.get('Ver Relatórios', False),
        'can_export_data': permissions.get('Exportar Dados', False),
    }
