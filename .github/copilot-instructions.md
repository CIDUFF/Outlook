# PROSPECTA - Instruções para Agentes IA

## Arquitetura do Sistema

**PROSPECTA** é um sistema Django 5.2+ de gestão de oportunidades e vendas com três camadas principais:

### Estrutura de Dados (Modelos)
- **UserProfile**: Extensão do Django User com roles (admin, gerente, vendedor, analista)
- **Client**: Empresa com CNPJ único, contatos relacionados
- **Opportunity**: Oportunidade de venda com status (aberta, em_andamento, ganha, perdida, cancelada)
- **Stage**: Etapas ordenadas dentro de uma oportunidade
- **Activity**: Tarefas dentro de etapas com aprovação obrigatória
- **History Models**: OpportunityHistory, StageHistory, ActivityHistory - rastreiam todas as mudanças

Padrão: UUIDs como PKs (exceto UserProfile), timestamps auto (created_at, updated_at), deletam em cascata.

### Fluxo de Autorização
1. **Role-based access**: Decorator `@role_required('admin', 'gerente', 'vendedor')` nas views
2. **Helper methods** em UserProfile: `is_admin()`, `is_manager()`, `is_seller()`
3. **Context helper** `get_user_context()` fornece permissões para templates
4. **Data filtering**: Views filtram querysets baseado no role - admins veem tudo, vendedores veem apenas seus dados

### Padrão HTMX + Tailwind
- **HTMX endpoints**: `/api/oportunidades/filtrar/`, `/api/oportunidades/<id>/status/` permitem atualizações parciais
- **Componentes reutilizáveis**: `prospecta/templates/prospecta/components/` (ex: opportunity_badge.html)
- **Tailwind CDN**: Carregado em base.html - estilos inline, sem build step necessário

## Padrões Críticos do Projeto

### Criar Novas Views
1. Usar `@login_required(login_url='account_login')` + `@role_required()` como decoradores
2. Começar com `context = get_user_context(request.user)` para permissões
3. Filtrar querysets: `opportunities = Opportunity.objects.filter(responsible_user=request.user)`
4. Registrar mudanças: Criar instância de *History após POST (exemplo: OpportunityHistory.objects.create(...))

### Editar Modelos
- Adicionar campos sempre com `blank=True, null=True` para segurança
- Adicionar `verbose_name` em português em cada campo
- Definir `db_table = 'tab_<nome>'` em Meta
- Usar `get_display()` em choices para labels em português

### Migração de Banco
```bash
uv run manage.py makemigrations
uv run manage.py migrate
```

## Configuração do Ambiente

**Stack**: Python 3.12+, PostgreSQL 12+, uv para package management

**Variáveis críticas** em `settings.py`:
- `LANGUAGE_CODE = 'pt-br'`, `TIME_ZONE = 'America/Sao_Paulo'`
- `LOGIN_REDIRECT_URL = 'prospecta:dashboard'` (redireciona após login)
- `DATABASES['default']` aponta para prospecta_user/outlook_user em localhost:5432

**Autenticação OAuth**: Google e GitHub via django-allauth. Configurar em `/admin/socialaccount/socialapp/`

## Comandos Essenciais

```bash
uv sync                           # Instalar dependências
uv run manage.py runserver 8555   # Iniciar servidor (port 8555)
uv run manage.py createsuperuser  # Criar admin
uv run manage.py shell            # Shell Django para queries
uv run manage.py collectstatic    # Coletar arquivos estáticos (produção)
```

## Integração Frontend-Backend

- **Templates**: Localizados em `prospecta/templates/prospecta/` com estrutura `{entity}/{action}.html` (ex: `opportunities/form.html`)
- **URL routing**: `prospecta/urls.py` - padrão `path('{action}/{param}/', views.{view_func}, name='{name}')`
- **Context comum**: Todas as views passam `is_admin`, `is_manager`, `is_seller` para condicionar UI
- **Messages**: Usar `messages.success()` e `messages.error()` para feedback ao usuário

## Troubleshooting Comum

- **Erro de permissão em views**: Verificar se user tem profile criado (`UserProfile.objects.get_or_create()`)
- **HTMX não atualiza**: Confirmar `hx-target`, `hx-swap` e resposta HTML está bem-formada
- **Estilos Tailwind não aparecem**: Confirmar script CDN está em base.html e não há CSS conflitante em staticfiles/
- **Status 403 em admin**: Confirmar `SITE_ID = 1` em settings e superusuário criado

## Convenções de Código

- **Nomes de função**: `snake_case`, views sufixadas com ação (create, update, delete, detail, list)
- **Nomes de modelo**: `PascalCase`
- **URLs**: Kebab-case em pathnames (ex: `/oportunidades/criar/` não `/oportunidades_criar/`)
- **Variáveis de contexto**: Sempre plural (ex: `opportunities`, `users`) quando lista
