"""Management command para auditoria de usuários e perfis"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from prospecta.models import UserProfile
from django.db import transaction


class Command(BaseCommand):
    help = 'Auditoria e correção de integridade do sistema de usuários'

    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true',
                            help='Corrigir inconsistências')
        parser.add_argument('--verbose', action='store_true',
                            help='Modo detalhado')

    def handle(self, *args, **options):
        fix = options['fix']
        verbose = options['verbose']

        self.stdout.write(self.style.SUCCESS(
            '=== AUDITORIA - USUÁRIOS E PERFIS ===\n'))

        # 1. Usuários sem profile
        self.check_users_without_profile(fix, verbose)

        # 2. Profiles órfãos
        self.check_orphan_profiles(fix, verbose)

        # 3. Usuários inativos
        self.check_inactive_users(verbose)

        # 4. Admins
        self.check_admins(verbose)

        # 5. Dados incompletos
        self.check_incomplete_profiles(verbose)

        # 6. Resumo
        self.print_summary()

    def check_users_without_profile(self, fix, verbose):
        """Verificar usuários sem UserProfile"""
        self.stdout.write(self.style.HTTP_INFO(
            '1️⃣  Verificando usuários sem profile...'))

        users_without_profile = User.objects.filter(profile__isnull=True)
        count = users_without_profile.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS(
                f'   ✓ Todos os {User.objects.count()} usuários têm profile\n'))
            return

        self.stdout.write(self.style.WARNING(
            f'   ⚠️  {count} usuário(s) SEM profile!\n'))

        if verbose:
            for user in users_without_profile:
                self.stdout.write(f'      - {user.username} ({user.email})')

        if fix:
            with transaction.atomic():
                for user in users_without_profile:
                    UserProfile.objects.create(user=user, role='visitante')
                    self.stdout.write(self.style.SUCCESS(
                        f'      ✓ Criado profile para {user.username}'))

    def check_orphan_profiles(self, fix, verbose):
        """Verificar profiles órfãos"""
        self.stdout.write(self.style.HTTP_INFO(
            '\n2️⃣  Verificando profiles órfãos...'))

        orphan_profiles = UserProfile.objects.filter(user__isnull=True)
        count = orphan_profiles.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS(
                '   ✓ Nenhum profile órfão\n'))
            return

        self.stdout.write(self.style.WARNING(
            f'   ⚠️  {count} profile(s) ÓRFÃO(s)!\n'))

        if fix:
            with transaction.atomic():
                deleted_count, _ = orphan_profiles.delete()
                self.stdout.write(self.style.SUCCESS(
                    f'      ✓ Deletados {deleted_count} profiles'))

    def check_inactive_users(self, verbose):
        """Verificar usuários inativos"""
        self.stdout.write(self.style.HTTP_INFO(
            '\n3️⃣  Verificando usuários inativos...'))

        inactive = UserProfile.objects.filter(is_active=False)
        count = inactive.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS(
                '   ✓ Nenhum usuário inativo\n'))
            return

        self.stdout.write(self.style.WARNING(
            f'   ⚠️  {count} usuário(s) INATIVO(s)\n'))

        if verbose:
            for profile in inactive:
                role_display = dict(UserProfile.ROLE_CHOICES).get(
                    profile.role, profile.role)
                self.stdout.write(
                    f'      - {profile.user.username} ({role_display})')

    def check_admins(self, verbose):
        """Verificar admins"""
        self.stdout.write(self.style.HTTP_INFO(
            '\n4️⃣  Verificando administradores...'))

        admins = UserProfile.objects.filter(role='admin')
        count = admins.count()

        if count == 0:
            self.stdout.write(self.style.ERROR(
                '   ❌ NENHUM ADMIN ENCONTRADO!\n'))
            return

        self.stdout.write(self.style.SUCCESS(f'   ✓ {count} admin(s)\n'))

        if verbose:
            for admin in admins:
                status = '✓' if admin.user.is_active else '✗'
                self.stdout.write(f'      - {admin.user.username} {status}')

    def check_incomplete_profiles(self, verbose):
        """Verificar dados incompletos"""
        self.stdout.write(self.style.HTTP_INFO(
            '\n5️⃣  Verificando profiles incompletos...'))

        issues = []

        users_no_name = User.objects.filter(
            first_name__exact='') | User.objects.filter(last_name__exact='')
        if users_no_name.exists():
            issues.append(f'Sem nome completo: {users_no_name.count()}')

        no_dept = UserProfile.objects.filter(
            department__exact='') | UserProfile.objects.filter(department__isnull=True)
        if no_dept.exists():
            issues.append(f'Sem departamento: {no_dept.count()}')

        if not issues:
            self.stdout.write(self.style.SUCCESS('   ✓ Tudo completo\n'))
            return

        self.stdout.write(self.style.WARNING(
            '   ⚠️  Problemas encontrados:\n'))
        for issue in issues:
            self.stdout.write(f'      - {issue}')

    def print_summary(self):
        """Resumo final"""
        self.stdout.write(self.style.SUCCESS('\n=== RESUMO ==='))

        total_users = User.objects.count()
        total_profiles = UserProfile.objects.count()
        active_profiles = UserProfile.objects.filter(is_active=True).count()

        self.stdout.write(f'Total de Usuários: {total_users}')
        self.stdout.write(f'Total de Profiles: {total_profiles}')
        self.stdout.write(f'Usuários Ativos: {active_profiles}')

        admins = UserProfile.objects.filter(role='admin').count()
        managers = UserProfile.objects.filter(role='gerente').count()
        analysts = UserProfile.objects.filter(role='analista').count()
        visitors = UserProfile.objects.filter(role='visitante').count()

        self.stdout.write('\nDistribuição:')
        self.stdout.write(f'  👑 Admins: {admins}')
        self.stdout.write(f'  💼 Gerentes: {managers}')
        self.stdout.write(f'  📊 Analistas: {analysts}')
        self.stdout.write(f'  👁️ Visitantes: {visitors}')

        if total_users == total_profiles:
            self.stdout.write(self.style.SUCCESS('\n✅ Sistema INTEGRO!'))
        else:
            self.stdout.write(self.style.ERROR(
                '\n❌ Inconsistência detectada!'))
