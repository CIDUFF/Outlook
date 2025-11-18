"""Management command para setup de OAuth"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Configurar SocialApp do Google para OAuth'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, help='Google Client ID')
        parser.add_argument('--secret', type=str, help='Google Secret')
        parser.add_argument('--domain', type=str,
                            default='localhost:8555', help='Domain')

    def handle(self, *args, **options):
        client_id = options.get('client_id')
        secret = options.get('secret')
        domain = options['domain']

        if not client_id:
            client_id = input('Google Client ID: ').strip()
        if not secret:
            secret = input('Google Secret: ').strip()

        self.stdout.write(self.style.HTTP_INFO('\n🔍 Configurando OAuth...\n'))

        # 1. Site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={'domain': domain, 'name': 'PROSPECTA'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(
                f'✓ Site criado: {site.domain}'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'✓ Site encontrado: {site.domain}'))

        # 2. Remover app anterior
        existing = SocialApp.objects.filter(provider='google')
        if existing.exists():
            self.stdout.write(self.style.WARNING(
                '⚠️  Removendo app Google anterior...'))
            existing.delete()

        # 3. Criar novo app
        app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth',
            client_id=client_id,
            secret=secret,
        )
        app.sites.add(site)

        self.stdout.write(self.style.SUCCESS('\n✓ SocialApp Google criado!'))
        self.stdout.write('  Provider: google')
        self.stdout.write('  Name: Google OAuth')
        self.stdout.write(f'  Client ID: {client_id[:30]}...')
        self.stdout.write(f'  Site: {site.domain}')
        self.stdout.write(self.style.SUCCESS(
            '\n✅ OAuth configurado com sucesso!\n'))
