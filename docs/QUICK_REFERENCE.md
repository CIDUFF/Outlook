# 📋 REFERÊNCIA RÁPIDA - PERMISSÕES PROSPECTA

## 🔐 Mapas de Acesso por Página

### Oportunidades

| Página | Admin | Gerente | Analista | Visitante |
|--------|-------|---------|----------|-----------|
| `/oportunidades/` | ✅ Todas | ✅ Suas | ✅ Suas | ❌ Bloqueado |
| `/oportunidades/criar/` | ✅ | ✅ | ❌ 403 | ❌ 403 |
| `/oportunidades/<id>/` | ✅ | ✅ | ✅ | ❌ 403 |
| `/oportunidades/<id>/editar/` | ✅ | ✅ | ❌ 403 | ❌ 403 |
| `/oportunidades/<id>/deletar/` | ✅ | ✅ | ❌ 403 | ❌ 403 |

### Clientes

| Página | Admin | Gerente | Analista | Visitante |
|--------|-------|---------|----------|-----------|
| `/clientes/` | ✅ Todas | ✅ Todas | ✅ Todas | ❌ Bloqueado |
| `/clientes/criar/` | ✅ | ✅ | ❌ 403 | ❌ 403 |
| `/clientes/<id>/` | ✅ | ✅ | ✅ | ❌ 403 |
| `/clientes/<id>/editar/` | ✅ | ✅ | ❌ 403 | ❌ 403 |

### Atividades

| Página | Admin | Gerente | Analista | Visitante |
|--------|-------|---------|----------|-----------|
| `/atividades/` | ✅ Todas | ✅ Suas + Delegadas | ✅ Suas | ❌ Bloqueado |
| `/atividades/<id>/aprovar/` | ✅ | ✅ | ❌ 403 | ❌ 403 |

### Admin

| Página | Admin | Gerente | Analista | Visitante |
|--------|-------|---------|----------|-----------|
| `/gerenciar/painel/` | ✅ | ❌ 403 | ❌ 403 | ❌ 403 |
| `/gerenciar/usuarios/` | ✅ | ❌ 403 | ❌ 403 | ❌ 403 |
| `/gerenciar/usuarios/criar/` | ✅ | ❌ 403 | ❌ 403 | ❌ 403 |

### Relatórios

| Página | Admin | Gerente | Analista | Visitante |
|--------|-------|---------|----------|-----------|
| `/relatorios/` | ✅ | ✅ | ✅ | ❌ 403 |

---

## 🎨 Template Conditionals

### Botões de Ação

```django
{# Criar novo #}
{% if can_write %}
    <a href="...criar...">Nova Oportunidade</a>
{% endif %}

{# Editar #}
{% if can_write %}
    <a href="...editar...">Editar</a>
{% endif %}

{# Deletar (mais restritivo) #}
{% if is_manager %}
    <a href="...deletar...">Deletar</a>
{% endif %}

{# Admin Panel #}
{% if is_admin %}
    <a href="/gerenciar/painel/">Administração</a>
{% endif %}
```

### Menu Dinâmico

```django
{# Mostrar/esconder itens do menu #}
{% if not is_visitor %}
    <li><a href="/oportunidades/">Oportunidades</a></li>
    <li><a href="/clientes/">Clientes</a></li>
{% endif %}

{% if is_manager or is_admin %}
    <li><a href="/atividades/">Atividades</a></li>
{% endif %}

{% if is_admin %}
    <li><a href="/gerenciar/painel/">Administração</a></li>
{% endif %}
```

---

## 🛡️ Decoradores Django

### Adicionar a uma View

```python
from django.contrib.auth.decorators import login_required
from prospecta.views import role_required, write_permission_required

# Apenas login obrigatório
@login_required(login_url='account_login')
def minha_view(request):
    pass

# Apenas admin/gerente
@login_required(login_url='account_login')
@role_required('admin', 'gerente')
def admin_view(request):
    pass

# Bloquear visitantes (qualquer papel menos visitante)
@login_required(login_url='account_login')
@write_permission_required
def create_view(request):
    pass

# Apenas admin
@login_required(login_url='account_login')
@role_required('admin')
def super_admin_view(request):
    pass
```

---

## 🔍 Métodos UserProfile

```python
user.profile.is_admin()        # True se role == 'admin'
user.profile.is_manager()       # True se role em ['admin', 'gerente']
user.profile.is_analyst()       # True se role em ['admin', 'gerente', 'analista']
user.profile.is_visitor()       # True se role == 'visitante'
user.profile.can_write()        # True se pode criar/editar/deletar
user.profile.can_read()         # True (todos podem ler)
user.profile.get_role_display() # String com nome legível do papel
```

---

## 📊 Contexto em Templates

```django
{# Disponível em qualquer template após get_user_context() #}
{{ is_admin }}        {# True/False #}
{{ is_manager }}      {# True/False #}
{{ is_analyst }}      {# True/False #}
{{ is_visitor }}      {# True/False #}
{{ can_write }}       {# True/False #}
{{ can_read }}        {# True/False (sempre True) #}
{{ user.profile.role }}{# String: admin, gerente, analista, visitante #}
{{ user.get_full_name }} {# Nome completo do usuário #}
```

---

## 🔀 Fluxo de Autenticação

```
┌─────────────────────────────────────────────────┐
│ Usuário acessa http://localhost:8555/xyz/      │
└───────────────┬─────────────────────────────────┘
                │
                ▼
        ┌──────────────────┐
        │  @login_required │
        │  Login é válido? │
        └────┬─────────┬───┘
             │         │
            NÃO       SIM
             │         │
             ▼         ▼
        Redirect   ┌──────────────────┐
        /login/    │  @role_required  │
                   │  Role permitida? │
                   └────┬─────────┬───┘
                       │         │
                      NÃO       SIM
                       │         │
                       ▼         ▼
                    403    ┌──────────────────┐
                    Error  │  @write_..._req  │
                           │  Pode escrever?  │
                           └────┬─────────┬───┘
                               │         │
                              NÃO       SIM
                               │         │
                               ▼         ▼
                            Bloqueio   ✅ View
                                      Executada
```

---

## 🧪 Testar Permissão

### Via Terminal

```bash
# Testar se página requer login
curl -I http://localhost:8555/oportunidades/

# Testar com credenciais
curl -b "sessionid=XXX" http://localhost:8555/oportunidades/

# Testar POST (criar)
curl -X POST http://localhost:8555/oportunidades/criar/ \
  -b "sessionid=XXX" \
  -d "title=Test"
```

### Via Django Shell

```bash
python manage.py shell

from django.contrib.auth.models import User
from prospecta.models import UserProfile

user = User.objects.get(username='gerente_teste')
profile = user.profile

# Verificar papel
print(profile.is_manager())  # True
print(profile.can_write())   # True
print(profile.role)          # 'gerente'
```

---

## 🚨 Troubleshooting

### Problema: Usuário vê erro 403
```
Solução: Verificar role do usuário
- Ir para /gerenciar/usuarios/
- Editar usuário e confirmar papel
- Fazer logout e login novamente
```

### Problema: Botão "Criar" visível para analista
```
Solução: Verificar template
- Confirmar {% if can_write %}
- Confirmar context tem 'can_write': True/False
- Limpar cache (Ctrl+F5)
```

### Problema: Função retorna 404 em vez de 403
```
Solução: Falta decorador
- Adicionar @login_required
- Adicionar @role_required se necessário
- Fazer migrate se mudou models
```

### Problema: Visitante acessa página
```
Solução: Adicionar validação
if profile.is_visitor():
    messages.error(request, 'Sem permissão')
    return redirect('prospecta:home')
```

---

## 📞 Contacts & Docs

**Documentação Completa:**
- `ANALYSIS_PERMISSIONS.md` - Problemas encontrados
- `SECURITY_AUDIT_REPORT.md` - Relatório detalhado
- `TESTING_GUIDE.md` - Guia de testes
- `PERMISSIONS_FIXED.md` - Resuma de correções

**Files Modified:**
- `prospecta/views.py` - Views com decoradores
- `prospecta/templates/**/*.html` - Templates protegidos
- `prospecta/models.py` - UserProfile com métodos

---

**Última Atualização:** 17 de novembro de 2025  
**Status:** ✅ PRONTO PARA PRODUÇÃO
