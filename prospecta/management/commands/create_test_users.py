"""Management command para criar usuários teste"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from prospecta.models import UserProfile


class Command(BaseCommand):
    help = 'Criar usuários de teste para o sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--gerente',
            action='store_true',
            help='Criar um gerente de teste',
        )
        parser.add_argument(
            '--analista',
            action='store_true',
            help='Criar um analista de teste',
        )

    def handle(self, *args, **options):
        if options['gerente']:
            self.create_manager()
        elif options['analista']:
            self.create_analyst()
        else:
            self.stdout.write(self.style.WARNING(
                'Use --gerente ou --analista'))

    def create_manager(self):
        """Criar gerente de teste"""
        if User.objects.filter(username='gerente').exists():
            self.stdout.write(self.style.WARNING('Gerente já existe'))
            return

        user = User.objects.create_user(
            username='gerente',
            email='gerente@test.com',
            password='gerente123',
            first_name='João',
            last_name='Gerente'
        )

        UserProfile.objects.create(
            user=user,
            role='gerente',
            department='Vendas',
            phone='(11) 99999-9999'
        )

        self.stdout.write(self.style.SUCCESS(
            f'✓ Gerente criado: {user.username}'))
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write('  Senha: gerente123')

    def create_analyst(self):
        """Criar analista de teste"""
        if User.objects.filter(username='analista').exists():
            self.stdout.write(self.style.WARNING('Analista já existe'))
            return

        user = User.objects.create_user(
            username='analista',
            email='analista@test.com',
            password='analista123',
            first_name='Maria',
            last_name='Analista'
        )

        UserProfile.objects.create(
            user=user,
            role='analista',
            department='Análise',
            phone='(11) 98888-8888'
        )

        self.stdout.write(self.style.SUCCESS(
            f'✓ Analista criado: {user.username}'))
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write('  Senha: analista123')
