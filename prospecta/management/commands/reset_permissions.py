"""
Comando para resetar as permissões da matriz para os valores padrão
"""
from django.core.management.base import BaseCommand
from prospecta.models import PermissionsMatrix


class Command(BaseCommand):
    help = 'Reseta a matriz de permissões para os valores padrão'

    def add_arguments(self, parser):
        parser.add_argument(
            '--role',
            type=str,
            help='Resetar apenas um role específico (admin, gerente, analista, visitante)',
        )

    def handle(self, *args, **options):
        # Definir permissões padrão por role
        default_permissions = {
            'admin': {
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
            },
            'gerente': {
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
            },
            'analista': {
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
            },
            'visitante': {
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

        # Verificar se foi especificado um role específico
        role_filter = options.get('role')
        if role_filter:
            if role_filter not in default_permissions:
                self.stdout.write(
                    self.style.ERROR(f'Role inválido: {role_filter}')
                )
                self.stdout.write(
                    self.style.WARNING('Roles válidos: admin, gerente, analista, visitante')
                )
                return

            roles_to_update = {role_filter: default_permissions[role_filter]}
        else:
            roles_to_update = default_permissions

        # Atualizar roles
        self.stdout.write(self.style.SUCCESS('Resetando permissões...'))
        
        for role, perms in roles_to_update.items():
            perm_obj, created = PermissionsMatrix.objects.update_or_create(
                role=role,
                defaults={'permissions': perms}
            )
            count_true = sum(1 for v in perms.values() if v)
            action = 'criado' if created else 'atualizado'
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'  {role.upper():12} -> {count_true}/{len(perms)} permissões '
                    f'habilitadas ({action})'
                )
            )

        self.stdout.write(self.style.SUCCESS('\n✓ Permissões resetadas com sucesso!'))
