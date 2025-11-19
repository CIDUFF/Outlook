#!/usr/bin/env python
"""Script para debugar problema de redirect_uri no OAuth Google"""
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.conf import settings
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Outlook.settings')
django.setup()


print("=" * 60)
print("DEBUG: OAUTH REDIRECT_URI MISMATCH")
print("=" * 60)

# 1. Configuração do Django
print("\n📋 CONFIGURAÇÃO DO DJANGO:")
print(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(
    f"  ACCOUNT_DEFAULT_HTTP_PROTOCOL: {settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}")
print(f"  CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
print(f"  SITE_ID: {settings.SITE_ID}")

# 2. Site registrado no banco
print("\n🏢 SITE REGISTRADO NO BANCO:")
try:
    site = Site.objects.get(id=settings.SITE_ID)
    print(f"  Domain: {site.domain}")
    print(f"  Name: {site.name}")
except Site.DoesNotExist:
    print(f"  ❌ ERRO: Site com ID {settings.SITE_ID} não encontrado!")

# 3. App Google
print("\n🔐 GOOGLE OAUTH APP:")
try:
    google_app = SocialApp.objects.get(provider='google')
    print(f"  Provider: {google_app.provider}")
    print(f"  Name: {google_app.name}")
    print(f"  Client ID: {google_app.client_id}")
    print(f"  Sites vinculados:")
    for s in google_app.sites.all():
        print(f"    - {s.domain}")
except SocialApp.DoesNotExist:
    print("  ❌ ERRO: Nenhum app Google configurado!")

# 4. Redirect URI que SERÁ gerado
print("\n✅ REDIRECT_URI QUE SERÁ GERADO:")
protocol = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
site_domain = site.domain
callback_path = '/accounts/google/login/callback/'
correct_uri = f"{protocol}://{site_domain}{callback_path}"
print(f"  {correct_uri}")

# 5. Redirect URI recebido (do erro)
print("\n❌ REDIRECT_URI DO ERRO:")
error_uri = "https://cid-uff.net:8555/accounts/google/login/callback/"
print(f"  {error_uri}")

# 6. Análise do problema
print("\n🔍 ANÁLISE DO PROBLEMA:")
if error_uri.replace(":8555", "") in [f"{protocol}://{site_domain}{callback_path}",
                                      f"{protocol}://cid-uff.net{callback_path}"]:
    print("  ✓ A porta 8555 é adicionada pela requisição HTTP")
    print("  → POSSÍVEL CAUSA: Nginx/Apache não está passando X-Forwarded-Proto corretamente")
    print("  → SOLUÇÃO: Configurar headers de proxy reverso no servidor web")
else:
    print("  ✓ Domínios não coincidem completamente")

if "cid-uff.net" in error_uri and "prospecta.cid-uff.net" not in error_uri:
    print("\n  ⚠️ ATENÇÃO: A requisição está usando cid-uff.net em vez de prospecta.cid-uff.net")
    print("  → POSSÍVEL CAUSA: Você tem múltiplos subdomínios apontando para o mesmo servidor")
    print("  → SOLUÇÃO: No Google Cloud, adicione AMBOS os URIs:")
    print("    • https://prospecta.cid-uff.net/accounts/google/login/callback/")
    print("    • https://cid-uff.net/accounts/google/login/callback/")

print("\n📝 AÇÃO RECOMENDADA:")
print("  1. No Console do Google Cloud, edite o OAuth Client")
print("  2. Em 'URIs de redirecionamento autorizados', adicione:")
print("     https://cid-uff.net/accounts/google/login/callback/")
print("     https://prospecta.cid-uff.net/accounts/google/login/callback/")
print("  3. Aguarde 5-10 minutos para propagar")
print("  4. Tente fazer login novamente")
print("\n" + "=" * 60)
