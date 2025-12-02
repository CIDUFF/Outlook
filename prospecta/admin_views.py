from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

from .models import UserProfile


def admin_required(view_func):
    """Decorator para verificar se é admin/superuser"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')

        # Verificar se é superuser ou admin
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin()):
            return view_func(request, *args, **kwargs)

        messages.error(
            request, 'Você não tem permissão para acessar esta página.')
        return redirect('prospecta:dashboard')
    return wrapper


@login_required(login_url='account_login')
@admin_required
def admin_dashboard(request):
    """Dashboard do painel administrativo"""
    context = {
        'page_title': 'Painel Administrativo',
        'total_users': User.objects.count(),
        'total_admins': UserProfile.objects.filter(role='admin').count(),
        'total_managers': UserProfile.objects.filter(role='gerente').count(),
        'total_analysts': UserProfile.objects.filter(role='analista').count(),
        'total_visitors': UserProfile.objects.filter(role='visitante').count(),
        'inactive_users': UserProfile.objects.filter(is_active=False).count(),
    }

    return render(request, 'prospecta/admin/dashboard.html', context)


@login_required(login_url='account_login')
@admin_required
def admin_users_list(request):
    """Listar todos os usuários"""
    # Filtros
    search = request.GET.get('search', '')
    role = request.GET.get('role', '')
    status = request.GET.get('status', '')

    users = User.objects.select_related('profile').all()

    if search:
        users = users.filter(Q(first_name__icontains=search)
                             | Q(email__icontains=search))

    if role:
        users = users.filter(profile__role=role)

    if status == 'active':
        users = users.filter(profile__is_active=True)
    elif status == 'inactive':
        users = users.filter(profile__is_active=False)

    context = {
        'page_title': 'Gerenciar Usuários',
        'users': users,
        'search': search,
        'role': role,
        'status': status,
        'role_choices': UserProfile.ROLE_CHOICES,
    }

    return render(request, 'prospecta/admin/users_list.html', context)


@login_required(login_url='account_login')
@admin_required
def admin_user_detail(request, user_id):
    """Detalhar e editar usuário"""
    user = get_object_or_404(User, id=user_id)
    profile = UserProfile.objects.get(user=user)

    if request.method == 'POST':
        # Atualizar dados do usuário
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        # Atualizar profile
        profile.role = request.POST.get('role', profile.role)
        profile.department = request.POST.get('department', profile.department)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.is_active = request.POST.get('is_active') == 'on'
        profile.save()

        # Sincronizar is_staff/is_superuser se for admin
        if profile.role == 'admin':
            user.is_staff = True
        else:
            user.is_staff = False
        user.save()

        messages.success(
            request, f'Usuário {user.first_name} atualizado com sucesso!')
        return redirect('prospecta:admin_users_list')

    context = {
        'page_title': f'Editar Usuário - {user.get_full_name()}',
        'user': user,
        'profile': profile,
        'role_choices': UserProfile.ROLE_CHOICES,
    }

    return render(request, 'prospecta/admin/user_detail.html', context)


@login_required(login_url='account_login')
@admin_required
def admin_user_delete(request, user_id):
    """Deletar usuário"""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        name = user.get_full_name() or user.username
        user.delete()
        messages.success(request, f'Usuário {name} deletado com sucesso!')
        return redirect('prospecta:admin_users_list')

    context = {
        'page_title': f'Deletar Usuário - {user.get_full_name()}',
        'user': user,
    }

    return render(request, 'prospecta/admin/user_delete_confirm.html', context)


@login_required(login_url='account_login')
@admin_required
def admin_user_toggle_status(request, user_id):
    """Toggle de ativo/inativo"""
    user = get_object_or_404(User, id=user_id)
    profile = UserProfile.objects.get(user=user)

    profile.is_active = not profile.is_active
    profile.save()

    status = "ativado" if profile.is_active else "desativado"
    messages.success(request, f'Usuário {status} com sucesso!')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'is_active': profile.is_active})

    return redirect('prospecta:admin_users_list')


@login_required(login_url='account_login')
@admin_required
def admin_create_user(request):
    """Criar novo usuário"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role = request.POST.get('role', 'vendedor')

        # Validações
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuário com este nome já existe!')
            return redirect('prospecta:admin_create_user')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email já cadastrado!')
            return redirect('prospecta:admin_create_user')

        # Criar usuário
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Criar profile (ou usar existente)
        UserProfile.objects.get_or_create(user=user, defaults={'role': role})

        # Se for admin, marcar como staff
        if role == 'admin':
            user.is_staff = True
            user.save()

        messages.success(request, f'Usuário {first_name} criado com sucesso!')
        return redirect('prospecta:admin_users_list')

    context = {
        'page_title': 'Criar Novo Usuário',
        'role_choices': UserProfile.ROLE_CHOICES,
    }

    return render(request, 'prospecta/admin/user_create.html', context)


@login_required(login_url='account_login')
@admin_required
@login_required(login_url='account_login')
@admin_required
def permissions_matrix(request):
    """Exibe e edita matriz de permissões por role"""

    # Definição de permissões padrão por role
    default_permissions_map = {
        'admin': {
            'label': 'Administrador',
            'color': 'red',
            'permissions': {
                'Gerenciar Usuários': True,
                'Acessar Painel Admin': True,
                'Criar Oportunidades': True,
                'Editar Oportunidades': True,
                'Deletar Oportunidades': True,
                'Atribuir Oportunidades': True,
                'Gerenciar Etapas': True,
                'Gerenciar Atividades': True,
                'Gerenciar Contatos': True,
                'Gerenciar Clientes': True,
                'Ver Relatórios': True,
                'Exportar Dados': True,
                'Configurar Sistema': True,
            }
        },
        'gerente': {
            'label': 'Gerente',
            'color': 'blue',
            'permissions': {
                'Gerenciar Usuários': False,
                'Acessar Painel Admin': False,
                'Criar Oportunidades': True,
                'Editar Oportunidades': True,
                'Deletar Oportunidades': False,
                'Atribuir Oportunidades': True,
                'Gerenciar Etapas': True,
                'Gerenciar Atividades': True,
                'Gerenciar Contatos': True,
                'Gerenciar Clientes': True,
                'Ver Relatórios': True,
                'Exportar Dados': True,
                'Configurar Sistema': False,
            }
        },
        'analista': {
            'label': 'Analista',
            'color': 'green',
            'permissions': {
                'Gerenciar Usuários': False,
                'Acessar Painel Admin': False,
                'Criar Oportunidades': True,
                'Editar Oportunidades': False,
                'Deletar Oportunidades': False,
                'Atribuir Oportunidades': False,
                'Gerenciar Etapas': False,
                'Gerenciar Atividades': False,
                'Gerenciar Contatos': False,
                'Gerenciar Clientes': False,
                'Ver Relatórios': True,
                'Exportar Dados': False,
                'Configurar Sistema': False,
            }
        },
        'visitante': {
            'label': 'Visitante',
            'color': 'gray',
            'permissions': {
                'Gerenciar Usuários': False,
                'Acessar Painel Admin': False,
                'Criar Oportunidades': False,
                'Editar Oportunidades': False,
                'Deletar Oportunidades': False,
                'Atribuir Oportunidades': False,
                'Gerenciar Etapas': False,
                'Gerenciar Atividades': False,
                'Gerenciar Contatos': False,
                'Gerenciar Clientes': False,
                'Ver Relatórios': False,
                'Exportar Dados': False,
                'Configurar Sistema': False,
            }
        }
    }

    # Se for POST, salvar as permissões
    if request.method == 'POST':
        from django.contrib import messages
        from django.utils.text import slugify

        # Processar cada role
        for role in ['admin', 'gerente', 'analista', 'visitante']:
            # Obter permissions para este role do POST
            permissions_dict = {}
            for permission in default_permissions_map[role]['permissions'].keys():
                # Usar slugify para manter consistência com o template
                field_name = f"{role}_{slugify(permission)}"
                # Checkbox marcado envia valor, desmarcado não envia nada
                permissions_dict[permission] = field_name in request.POST

            # Salvar no banco (ou atualizar se existir)
            from .models import PermissionsMatrix
            perm_obj, created = PermissionsMatrix.objects.update_or_create(
                role=role,
                defaults={'permissions': permissions_dict}
            )

        messages.success(request, 'Permissões salvas com sucesso!')
        return redirect('prospecta:permissions_matrix')

    # Carregar permissões do banco de dados (se existirem) ou usar padrões
    from .models import PermissionsMatrix
    permissions_map = {}
    for role in ['admin', 'gerente', 'analista', 'visitante']:
        try:
            perm_obj = PermissionsMatrix.objects.get(role=role)
            permissions_map[role] = default_permissions_map[role].copy()
            permissions_map[role]['permissions'] = perm_obj.permissions
        except PermissionsMatrix.DoesNotExist:
            permissions_map[role] = default_permissions_map[role]

    # Obter todas as permissões únicas
    all_permissions = set()
    for role_perms in permissions_map.values():
        all_permissions.update(role_perms['permissions'].keys())
    all_permissions = sorted(list(all_permissions))

    context = {
        'page_title': 'Matriz de Permissões',
        'permissions_map': permissions_map,
        'all_permissions': all_permissions,
        'roles': ['admin', 'gerente', 'analista', 'visitante'],
    }

    return render(request, 'prospecta/admin/permissions_matrix.html', context)


@login_required(login_url='account_login')
@admin_required
def admin_help(request):
    """Página de ajuda e documentação para administradores"""
    context = {
        'page_title': 'Ajuda e Documentação',
        'total_users': User.objects.count(),
        'total_opportunities': 0,  # Será importado conforme necessário
        'system_version': '1.0.0',
    }

    return render(request, 'prospecta/admin/help.html', context)
