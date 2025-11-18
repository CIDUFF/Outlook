"""
Utilities for navigation, breadcrumbs, and common helper functions
"""
from django.urls import reverse


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
    Get common context variables for all views
    Includes permission checks and user role info
    """
    if not user or not hasattr(user, 'profile'):
        return {
            'is_admin': False,
            'is_manager': False,
            'is_analista': False,
            'is_visitor': True,
        }

    profile = user.profile
    is_admin = profile.role == 'admin'
    is_manager = profile.role == 'gerente'
    is_analista = profile.role == 'analista'
    is_visitor = profile.role == 'visitante'

    return {
        'is_admin': is_admin,
        'is_manager': is_manager,
        'is_analista': is_analista,
        'is_visitor': is_visitor,
        'user_role': profile.get_role_display(),
    }
