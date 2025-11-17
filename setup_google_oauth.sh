#!/bin/bash

# Script para configurar OAuth Google no PROSPECTA
# Uso: bash setup_google_oauth.sh <CLIENT_ID> <CLIENT_SECRET>

if [ $# -ne 2 ]; then
    echo "Uso: bash setup_google_oauth.sh <CLIENT_ID> <CLIENT_SECRET>"
    echo ""
    echo "Exemplo:"
    echo "  bash setup_google_oauth.sh 123456.apps.googleusercontent.com 'seu_secret_aqui'"
    exit 1
fi

CLIENT_ID=$1
CLIENT_SECRET=$2

echo "================================"
echo "PROSPECTA - Configurar Google OAuth"
echo "================================"
echo ""
echo "Client ID: $CLIENT_ID"
echo "Client Secret: ${CLIENT_SECRET:0:10}..."
echo ""

# Verificar se o servidor está rodando
echo "Verificando servidor Django..."
if ! curl -s http://localhost:8555/ > /dev/null 2>&1; then
    echo "⚠️  Servidor não está rodando em http://localhost:8555"
    echo "Inicie com: uv run manage.py runserver 8555"
    exit 1
fi
echo "✓ Servidor está rodando"

# Criar script Django para adicionar SocialApp
cat > /tmp/add_google_oauth.py << 'EOF'
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Outlook.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Obter ou criar Site
site, _ = Site.objects.get_or_create(
    pk=1,
    defaults={'domain': '127.0.0.1:8555', 'name': 'PROSPECTA'}
)
print(f"✓ Site configurado: {site.domain}")

# Obter ou criar SocialApp do Google
social_app, created = SocialApp.objects.get_or_create(
    provider='google',
    defaults={
        'name': 'Google OAuth',
        'client_id': sys.argv[1],
        'secret': sys.argv[2],
    }
)

if not created:
    social_app.client_id = sys.argv[1]
    social_app.secret = sys.argv[2]
    social_app.save()
    print("✓ SocialApp do Google atualizada")
else:
    print("✓ SocialApp do Google criada")

# Adicionar Site à SocialApp
if site not in social_app.sites.all():
    social_app.sites.add(site)
    print(f"✓ Site {site.domain} adicionado à SocialApp")

print("")
print("✅ Google OAuth configurado com sucesso!")
print("")
print("Próximas etapas:")
print("1. Acesse http://localhost:8555/accounts/login/")
print("2. Clique no botão 'Google'")
print("3. Autorize o acesso com sua conta Google")
EOF

echo ""
echo "Adicionando credenciais ao banco de dados..."
cd /home/marcus/desenvolvimento/Outlook && python /tmp/add_google_oauth.py "$CLIENT_ID" "$CLIENT_SECRET"

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✅ Configuração Completa!"
    echo "================================"
    echo ""
    echo "Seus botões de Google OAuth já estão visíveis em:"
    echo "  • Login: http://localhost:8555/accounts/login/"
    echo "  • Signup: http://localhost:8555/accounts/signup/"
else
    echo ""
    echo "❌ Erro ao configurar. Tente novamente."
    exit 1
fi
