#!/usr/bin/env python
"""Script para configurar SocialApp do Google"""
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Outlook.settings')
django.setup()


# Dados do Google OAuth (substituir com seus valores)
GOOGLE_CLIENT_ID = input("Insira o Google Client ID: ").strip()
GOOGLE_SECRET = input("Insira o Google Secret: ").strip()

print("\n🔍 Configurando Social App do Google...\n")

# 1. Verificar/Criar Site
site, created = Site.objects.get_or_create(
    id=1,
    defaults={'domain': 'localhost:8555', 'name': 'PROSPECTA'}
)
print(f"{'✓' if not created else '+'} Site: {site.domain}")

# 2. Remover app anterior se existir
existing = SocialApp.objects.filter(provider='google').first()
if existing:
    print(f"⚠️  Removendo app Google anterior...")
    existing.delete()

# 3. Criar novo SocialApp
app = SocialApp.objects.create(
    provider='google',
    name='Google OAuth',
    client_id=GOOGLE_CLIENT_ID,
    secret=GOOGLE_SECRET,
)

# 4. Adicionar site
app.sites.add(site)

print(f"✓ App Google criado com sucesso!")
print(f"  Client ID: {app.client_id[:30]}...")
print(f"  Site: {site.domain}")

print("\n✅ Configuração concluída!")
print("Agora você pode fazer login com Google!")
