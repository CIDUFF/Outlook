# 🎯 PROSPECTA - Sistema de Gestão de Oportunidades de Vendas

> **Plataforma moderna para gestão integrada de oportunidades e vendas com autenticação OAuth 2.0, permissões granulares e painel administrativo completo.**

---

## 📋 Sumário

- [🚀 Início Rápido](#-início-rápido)
- [📦 Tecnologias](#-tecnologias)
- [🏗️ Arquitetura](#️-arquitetura)
- [⚙️ Configuração](#️-configuração)
- [📚 Documentação Completa](#-documentação-completa)
- [👥 Roles e Permissões](#-roles-e-permissões)
- [🔒 Segurança](#-segurança)
- [📊 Painel de Administração](#-painel-de-administração)
- [🆘 Troubleshooting](#-troubleshooting)

---

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.12+
- PostgreSQL 12+
- `uv` package manager

### 1️⃣ Instalação

```bash
# Clonar repositório
git clone https://github.com/CIDLAGOAVIVA/Outlook.git
cd Outlook

# Sincronizar dependências
uv sync

# Copiar configuração de ambiente
cp .env.example .env

# Editar .env com suas credenciais
nano .env
```

### 2️⃣ Banco de Dados

```bash
# Criar banco (PostgreSQL)
createdb prospecta
createuser prospecta_user

# Aplicar migrações
uv run manage.py migrate

# Criar superuser
uv run manage.py createsuperuser
```

### 3️⃣ OAuth Google (Opcional)

```bash
# Script interativo para configurar Google OAuth
uv run setup_oauth.py

# Insira seu Client ID e Secret quando solicitado
```

### 4️⃣ Rodar o Servidor

```bash
# Desenvolvimento
uv run manage.py runserver 0.0.0.0:8555

# Produção (com Gunicorn)
gunicorn Outlook.wsgi --bind 0.0.0.0:8555
```

Acesse: **http://localhost:8555**

---

## 📦 Tecnologias

| Componente | Tecnologia |
|-----------|-----------|
| **Backend** | Django 5.2+ |
| **Frontend** | HTML5 + HTMX + Tailwind CSS |
| **Banco de Dados** | PostgreSQL 12+ |
| **Autenticação** | Django-allauth + OAuth 2.0 (Google/GitHub) |
| **Package Manager** | uv |
| **Web Server** | Apache 2.4 (Produção) |

---

## 🏗️ Arquitetura

### Estrutura de Pastas

```
Outlook/
├── Outlook/                 # Configurações Django
│   ├── settings.py         # Settings gerais + OAuth
│   ├── urls.py             # URLs principais
│   └── wsgi.py             # WSGI para produção
├── prospecta/              # App principal
│   ├── models.py           # Modelos: Opportunity, Client, Activity, etc
│   ├── views.py            # Views: CRUD + API HTMX
│   ├── admin_views.py      # Painel administrativo
│   ├── calendar_views.py   # Integração de calendário
│   ├── utils.py            # Helpers e utilidades
│   ├── signals.py          # Signals: auditoria automática
│   ├── adapters.py         # CustomSocialAccountAdapter
│   ├── migrations/         # Histórico de mudanças no BD
│   ├── templates/          # Templates HTML
│   └── static/             # CSS, JS, imagens
├── templates/              # Templates globais (login, base)
├── docs/                   # Documentação completa
│   ├── ENV_SETUP.md       # Variáveis de ambiente
│   ├── GET_STARTED.md     # Guia de início rápido
│   ├── ADMIN_PANEL.md     # Painel administrativo
│   ├── PERMISSIONS_FIXED.md # Sistema de permissões
│   └── ...
├── manage.py              # CLI do Django
└── pyproject.toml         # Dependências do projeto
```

### Modelos Principais

```
┌─────────────────────────────────────────────────┐
│         PROSPECTA Data Model                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  User (Django)                                  │
│    └── UserProfile (roles: admin, manager,     │
│        vendor, analyst)                         │
│                                                 │
│  Client (Empresa)                               │
│    ├── name (razão social)                     │
│    ├── cnpj (único)                            │
│    ├── segment, status                         │
│    └── contacts (related)                      │
│                                                 │
│  Opportunity                                    │
│    ├── title, description                      │
│    ├── client (FK)                             │
│    ├── responsible_user (FK)                   │
│    ├── status (open, in_progress, won, lost)  │
│    ├── stages (ordered list)                   │
│    ├── partnerships (M2M)                      │
│    └── history (OpportunityHistory)            │
│                                                 │
│  Stage                                          │
│    ├── opportunity (FK)                        │
│    ├── order (posição)                         │
│    ├── activities (related)                    │
│    └── history (StageHistory)                  │
│                                                 │
│  Activity                                       │
│    ├── stage (FK)                              │
│    ├── title, description                      │
│    ├── type (task, meeting, call)             │
│    ├── status (pending, approved, rejected)   │
│    ├── responsible_user (FK)                   │
│    ├── meeting (integrated)                    │
│    ├── attachments                             │
│    └── history (ActivityHistory)               │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## ⚙️ Configuração

### Variáveis de Ambiente (`.env`)

```env
# Django
DEBUG=False
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=prospecta.cid-uff.net,cid-uff.net

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=prospecta
DB_USER=prospecta_user
DB_PASSWORD=sua-senha-aqui
DB_HOST=localhost
DB_PORT=5432

# Email (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app-16-chars

# OAuth Google
GOOGLE_CLIENT_ID=seu-id-aqui.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-secret-aqui

# Site
SITE_ID=1
LANGUAGE_CODE=pt-br
TIME_ZONE=America/Sao_Paulo
ACCOUNT_DEFAULT_HTTP_PROTOCOL=https
```

**📖 Ver [docs/ENV_SETUP.md](docs/ENV_SETUP.md) para mais detalhes.**

### Apache Proxy Reverso (Produção)

```apache
<VirtualHost *:443>
    ServerName prospecta.cid-uff.net
    ServerAlias www.prospecta.cid-uff.net

    # Proxy para Django em localhost:8555
    ProxyPreserveHost On
    ProxyPass / http://localhost:8555/
    ProxyPassReverse / http://localhost:8555/

    # Headers para OAuth2 funcionar
    RequestHeader set X-Forwarded-Proto "https"

    SSLCertificateFile /etc/letsencrypt/live/prospecta.cid-uff.net/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/prospecta.cid-uff.net/privkey.pem
</VirtualHost>
```

### Django Settings (OAuth)

```python
# settings.py
USE_X_FORWARDED_PROTO = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_ADAPTER = 'prospecta.adapters.CustomSocialAccountAdapter'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
```

---

## 👥 Roles e Permissões

### Tipos de Usuários

| Role | Descrição | Permissões |
|------|-----------|-----------|
| **admin** | Administrador do sistema | Acesso total: CRUD, configurações, auditoria |
| **manager** | Gerente de vendas | Visibilidade total, aprova atividades, relatórios |
| **seller** | Vendedor | Vê apenas suas oportunidades, cria atividades |
| **analyst** | Analista | Leitura de dados, não pode editar |

### Decoradores de Autorização

```python
from prospecta.views import role_required

@login_required
@role_required('admin', 'manager')
def sensitive_view(request):
    return render(request, 'template.html')
```

### Filtragem de Dados

```python
# Views filtram querysets por role automaticamente
opportunities = Opportunity.objects.all()

if not request.user.is_admin():
    opportunities = opportunities.filter(responsible_user=request.user)
```

**📖 Ver [docs/PERMISSIONS_FIXED.md](docs/PERMISSIONS_FIXED.md) para sistema completo.**

---

## 📊 Painel de Administração

### Acesso
- **URL**: `/admin/painel/`
- **Requisito**: Role `admin` ou `manager`

### Funcionalidades

✅ **Dashboard com Estatísticas**
- Total de oportunidades por status
- Atividades pendentes
- Performance por vendedor
- Gráficos e métricas

✅ **Gerenciamento de Usuários**
- Criar, editar, deletar usuários
- Atribuir roles e permissões
- Ativar/desativar acesso
- Auditoria de ações

✅ **Auditoria Completa**
- Histórico de todas as mudanças
- Quem fez o quê e quando
- Rastreabilidade total

✅ **Relatórios**
- Oportunidades por status
- Performance de vendedores
- Análise de funil de vendas

**📖 Ver [docs/ADMIN_PANEL.md](docs/ADMIN_PANEL.md) para guia completo.**

---

## 🔒 Segurança

### Implementações

✅ **Autenticação**
- OAuth 2.0 com Google/GitHub
- Senhas hasheadas com PBKDF2
- Sessions seguras com tokens

✅ **Autorização**
- Role-based access control (RBAC)
- Filtragem de dados por role
- Decoradores de permissão

✅ **Proteção de Dados**
- CSRF tokens em todos os formulários
- X-Frame-Options para clickjacking
- SQL injection prevention (ORM)
- XSS protection (template escaping)

✅ **Auditoria**
- Histórico de todas as mudanças
- Logs de acesso administrativo
- Middleware de auditoria

✅ **Proxy Reverso**
- HTTPS obrigatório (Let's Encrypt)
- Headers de segurança
- X-Forwarded-* corretos

**📖 Ver [docs/SECURITY_AUDIT_REPORT.md](docs/SECURITY_AUDIT_REPORT.md).**

---

## 📚 Documentação Completa

### 📘 Guias de Início

- **[docs/GET_STARTED.md](docs/GET_STARTED.md)** - Setup inicial e primeiros passos
- **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Referência rápida de comandos

### 🔧 Configuração

- **[docs/ENV_SETUP.md](docs/ENV_SETUP.md)** - Variáveis de ambiente
- **[docs/ADMIN_SETUP.md](docs/ADMIN_SETUP.md)** - Setup do painel admin

### 👥 Permissões e Auditoria

- **[docs/PERMISSIONS_FIXED.md](docs/PERMISSIONS_FIXED.md)** - Sistema de permissões
- **[docs/AUDIT_USUARIOS.md](docs/AUDIT_USUARIOS.md)** - Auditoria de usuários
- **[docs/AUDITORIA_COMPLETA.md](docs/AUDITORIA_COMPLETA.md)** - Auditoria completa

### 📊 Administração

- **[docs/ADMIN_PANEL.md](docs/ADMIN_PANEL.md)** - Painel administrativo
- **[docs/GUIA_RAPIDO_ADMINISTRADOR.md](docs/GUIA_RAPIDO_ADMINISTRADOR.md)** - Guia rápido para admins

### 🎯 Negócio

- **[docs/FLUXO_REGRAS_NEGOCIO.md](docs/FLUXO_REGRAS_NEGOCIO.md)** - Fluxo e regras de negócio
- **[docs/PARCERIAS_FEATURE.md](docs/PARCERIAS_FEATURE.md)** - Feature de parcerias

### 🔒 Segurança

- **[docs/SECURITY_AUDIT_REPORT.md](docs/SECURITY_AUDIT_REPORT.md)** - Relatório de segurança
- **[docs/SECURITY_FIXES.md](docs/SECURITY_FIXES.md)** - Correções de segurança

### 🧪 Testes

- **[docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)** - Guia de testes

---

## 🆘 Troubleshooting

### ❌ OAuth `redirect_uri_mismatch`

**Sintoma**: Erro ao fazer login com Google

**Solução**:
1. Verifique `ALLOWED_HOSTS` no `.env`
2. Confirme `Site.domain` no Django admin
3. Registre redirect URIs no Google Cloud Console:
   ```
   https://prospecta.cid-uff.net/accounts/google/login/callback/
   https://cid-uff.net/accounts/google/login/callback/
   ```
4. Verifique headers do Apache (X-Forwarded-Proto)
5. Aguarde 5-10 minutos para propagar

**📖 Ver [docs/ENV_SETUP.md](docs/ENV_SETUP.md#obter-credenciais).**

### ❌ Erro de Permissão (403)

**Sintoma**: "Você não tem permissão para acessar"

**Solução**:
1. Verifique role do usuário: `user.userprofile.role`
2. Confirme se `UserProfile` existe: `UserProfile.objects.get_or_create(user=request.user)`
3. Cheque decorador `@role_required()` na view

### ❌ Banco de Dados Desconectado

**Sintoma**: `psycopg2.OperationalError: connection refused`

**Solução**:
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Conectar ao banco
psql -U prospecta_user -d prospecta -h localhost
```

### ❌ Migrações com Erro

**Sintoma**: `django.db.utils.ProgrammingError`

**Solução**:
```bash
# Listar migrações
uv run manage.py showmigrations

# Revertir até uma migração específica
uv run manage.py migrate prospecta 0001

# Re-aplicar
uv run manage.py migrate
```

### ❌ Static Files Não Carregam

**Sintoma**: CSS/JS não aparecem em produção

**Solução**:
```bash
# Coletar static files
uv run manage.py collectstatic --noinput

# Verificar permissões
chmod -R 755 staticfiles_collected/
```

---

## 📞 Comandos Úteis

```bash
# Gerenciamento
uv sync                          # Instalar dependências
uv run manage.py migrate         # Aplicar migrações
uv run manage.py createsuperuser # Criar admin
uv run manage.py runserver 8555  # Dev server

# Banco de Dados
uv run manage.py shell           # Django shell
uv run manage.py dbshell         # PostgreSQL shell

# Testes
uv run manage.py test prospecta  # Rodar testes

# Utilidades
uv run setup_oauth.py            # Configurar OAuth Google
uv run manage.py collectstatic   # Coletar assets estáticos

# Produção
gunicorn Outlook.wsgi --bind 0.0.0.0:8555
sudo systemctl restart prospecta # Reiniciar serviço
```

---

## 🤝 Contribuindo

1. Crie uma branch: `git checkout -b feature/sua-feature`
2. Faça as mudanças
3. Commit: `git commit -am 'Add nova feature'`
4. Push: `git push origin feature/sua-feature`
5. Abra um Pull Request

---

## 📝 Convenções de Código

### Python
- PEP 8 (Black formatter)
- Docstrings em português
- Type hints quando possível

### Django
- Views sufixadas com ação: `create`, `update`, `delete`, `list`, `detail`
- Modelos em PascalCase
- URLs em kebab-case: `/oportunidades/criar/`

### HTML/Templates
- Tailwind CSS para styling
- HTMX para interatividade
- Componentes reutilizáveis em `templates/components/`

---

## 📄 Licença

Este projeto é propriedade de **CID-UFF** e está sob licença privada.

---

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique a **[documentação](docs/)**
2. Consulte **[Troubleshooting](#-troubleshooting)**
3. Entre em contato com o time de desenvolvimento

---

**Desenvolvido com ❤️ por CID-UFF | Última atualização: Nov 2025**
