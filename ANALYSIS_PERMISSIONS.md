# 🔒 ANÁLISE DE PERMISSÕES - PROSPECTA

## Resultado da Auditoria de Segurança

### ⚠️ PROBLEMAS ENCONTRADOS

#### 1. **OPORTUNIDADES**

| View | Status | Problema | Deve Ter |
|------|--------|----------|----------|
| `opportunities_list()` | ❌ SEM PROTEÇÃO | Sem `@login_required` | Qualquer um logado pode ver |
| `opportunity_create()` | ✅ COM @role_required | Permite `vendedor` | Apenas `admin` e `gerente` |
| `opportunity_detail()` | ❌ SEM PROTEÇÃO | Sem `@login_required` | Qualquer um logado pode ver |
| `opportunity_update()` | ❌ SEM PROTEÇÃO | Sem decoradores | Apenas `admin` e `gerente` |
| `opportunity_delete()` | ✅ COM @role_required | OK | Apenas `admin` e `gerente` ✓ |
| `opportunity_status_update()` | ❌ SEM PROTEÇÃO | Sem decoradores | Apenas responsável + admin/gerente |

**PROBLEMA:** Analistas e visitantes podem criar/editar oportunidades!

---

#### 2. **CLIENTES**

| View | Status | Problema | Deve Ter |
|------|--------|----------|----------|
| `clients_list()` | ❌ SEM PROTEÇÃO | Sem `@login_required` | `admin`, `gerente` |
| `client_create()` | ❌ SEM PROTEÇÃO | Sem decoradores | `admin`, `gerente` apenas |
| `client_detail()` | ❌ SEM PROTEÇÃO | Sem `@login_required` | `admin`, `gerente`, `analista` |
| `client_update()` | ✅ COM @role_required | OK | Apenas `admin` e `gerente` ✓ |

**PROBLEMA:** Visitantes podem criar/editar clientes!

---

#### 3. **ATIVIDADES**

| View | Status | Problema | Deve Ter |
|------|--------|----------|----------|
| `activities_list()` | ❌ SEM PROTEÇÃO | Sem `@login_required` | Qualquer um logado |
| `activity_approve()` | ✅ COM @role_required | OK | Apenas `admin` e `gerente` ✓ |

**PROBLEMA:** Visitantes podem ver atividades (não deveriam!)

---

#### 4. **RELATÓRIOS**

| View | Status | Problema | Deve Ter |
|------|--------|----------|----------|
| `reports()` | ❌ SEM PROTEÇÃO | Sem decoradores | `admin`, `gerente`, `analista` |

**PROBLEMA:** Visitantes podem acessar relatórios!

---

### 🎯 MAPEAMENTO DE PAPÉIS

#### **ADMIN**
- ✅ Criar/editar/deletar tudo
- ✅ Gerenciar usuários (admin panel)
- ✅ Ver todos os relatórios
- ✅ Aprovar atividades
- ✅ Criar clientes

#### **GERENTE**
- ✅ Criar/editar/deletar oportunidades
- ✅ Criar/editar clientes
- ✅ Ver atividades próprias + delegadas
- ✅ Aprovar atividades
- ✅ Ver relatórios
- ❌ NÃO gerencia usuários

#### **ANALISTA**
- ✅ Ler oportunidades (filtradas)
- ✅ Ler clientes
- ✅ Ler atividades atribuídas
- ✅ Ver relatórios
- ❌ NÃO pode criar oportunidades
- ❌ NÃO pode criar clientes
- ❌ NÃO pode deletar nada
- ❌ NÃO pode editar oportunidades/clientes

#### **VISITANTE (Novo Usuário)**
- ✅ Ler apenas dashboard público
- ❌ NÃO pode ver oportunidades
- ❌ NÃO pode ver clientes
- ❌ NÃO pode ver atividades
- ❌ NÃO pode ver relatórios
- ❌ NÃO pode criar nada

---

### 📋 FORMULÁRIOS NO FRONTEND

**Onde devem ser escondidos:**

1. **Opportunities Form** (`opportunities/form.html`)
   - ❌ Esconder para visitantes
   - ❌ Esconder para analistas
   - ✅ Mostrar para admin/gerente

2. **Clients Form** (`clients/form.html`)
   - ❌ Esconder para visitantes
   - ❌ Esconder para analistas
   - ✅ Mostrar para admin/gerente

3. **Delete Buttons**
   - ❌ Esconder para analistas
   - ✅ Mostrar para admin/gerente

4. **Approval Buttons**
   - ❌ Esconder para analistas
   - ✅ Mostrar para admin/gerente

---

### 🔧 SOLUÇÕES NECESSÁRIAS

#### Backend (Views)
```python
# Adicionar @login_required + @write_permission_required
@login_required(login_url='account_login')
@write_permission_required  # Analistas + visitantes bloqueados
def opportunity_create(request):
    ...

# Para leitura, permitir admin/gerente/analista
@login_required(login_url='account_login')
def opportunities_list(request):
    # Mas filtrar visitors
    if profile.is_visitor():
        return redirect('prospecta:home')
    ...
```

#### Frontend (Templates)
```django
{% if not is_visitor and can_write %}
    <a href="...criar..." class="btn">Criar Oportunidade</a>
{% endif %}
```

---

## ✅ CHECKLIST DE CORREÇÕES

- [ ] Adicionar `@login_required` em todas as views
- [ ] Adicionar `@write_permission_required` em CREATE/UPDATE/DELETE
- [ ] Adicionar role checks para visitantes em LIST views
- [ ] Esconder botões CREATE em templates para analistas
- [ ] Esconder botões DELETE em templates para analistas
- [ ] Esconder formulários de edição para analistas
- [ ] Testar acesso com cada papel
- [ ] Testar redirecionamento para visitantes

---

## 📝 STATUS

**PRIORIDADE:** 🔴 CRÍTICA  
**IMPACTO:** Alta segurança em risco  
**ESFORÇO:** Baixo (~30 minutos)

