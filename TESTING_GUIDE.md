# 🧪 GUIA DE TESTES - SISTEMA DE PERMISSÕES

## Prepare-se para Testar

### 1. Criar Usuários de Teste (via admin panel)

```bash
# Login como admin (superuser)
url: http://localhost:8555/gerenciar/painel/
usuario: seu_admin_user
```

Depois, ir para `/gerenciar/usuarios/criar/` e criar:

**Usuário 1: Gerente**
- Username: `gerente_teste`
- Email: `gerente@test.com`
- Papel: `Gerente`

**Usuário 2: Analista**
- Username: `analista_teste`
- Email: `analista@test.com`
- Papel: `Analista`

**Usuário 3: Visitante**
- Username: `visitante_teste`
- Email: `visitante@test.com`
- Papel: `Visitante`

---

## 🧪 Teste 1: VISITANTE (Deve estar bloqueado)

### Login como visitante_teste

1. **Acessar `/oportunidades/`**
   - ✅ Esperado: Mensagem de erro + redirecionamento para `/dashboard/`
   - Erro: "Você não tem permissão para acessar oportunidades."
   - ❌ Se: Vê lista de oportunidades → BUG!

2. **Acessar `/clientes/`**
   - ✅ Esperado: Mensagem de erro + redirecionamento
   - ❌ Se: Vê lista de clientes → BUG!

3. **Acessar `/atividades/`**
   - ✅ Esperado: Mensagem de erro + redirecionamento
   - ❌ Se: Vê atividades → BUG!

4. **Acessar `/relatorios/`**
   - ✅ Esperado: Mensagem de erro + redirecionamento
   - ❌ Se: Vê relatórios → BUG!

5. **Menu deve estar vazio**
   - ✅ Esperado: Apenas "Dashboard" e "Perfil" no menu
   - ❌ Se: Vê outros itens → BUG!

---

## 🧪 Teste 2: ANALISTA (Leitura apenas)

### Login como analista_teste

1. **Acessar `/oportunidades/`**
   - ✅ Esperado: Vê oportunidades atribuídas
   - ❌ Se: Vê todas as oportunidades → Filtro errado!

2. **Procurar botão "Nova Oportunidade"**
   - ✅ Esperado: Botão NÃO existe
   - ❌ Se: Vê botão → Template errado!

3. **Em uma oportunidade, procurar por "Editar"**
   - ✅ Esperado: Botão NÃO existe
   - ❌ Se: Vê botão → Template errado!

4. **Acessar URL direta `/oportunidades/<id>/editar/`**
   - ✅ Esperado: Erro 403 (Forbidden)
   - Mensagem: "Você não tem permissão para acessar"
   - ❌ Se: Carrega formulário → Decorador não está funcionando!

5. **Acessar `/clientes/`**
   - ✅ Esperado: Vê lista de clientes
   - ✅ Botão "Novo Cliente" NÃO deve estar visível
   - ❌ Se: Vê botão → BUG!

6. **Acessar `/relatorios/`**
   - ✅ Esperado: Vê página de relatórios
   - ❌ Se: Erro 403 → Decorador está restringindo demais!

---

## 🧪 Teste 3: GERENTE (Acesso completo delegado)

### Login como gerente_teste

1. **Acessar `/oportunidades/`**
   - ✅ Esperado: Vê suas oportunidades (criadas ou responsável)
   - ✅ Botão "Nova Oportunidade" deve estar visível
   - ❌ Se: Vê todas as oportunidades → Filtro errado!

2. **Clicar em "Nova Oportunidade"**
   - ✅ Esperado: Carrega formulário de criação
   - ✅ Pode preencher e criar
   - ❌ Se: Erro 403 → Decorador muito restritivo!

3. **Editar uma oportunidade**
   - ✅ Esperado: Botão "Editar" visível
   - ✅ Pode editar e salvar
   - ❌ Se: Erro → BUG!

4. **Deletar uma oportunidade**
   - ✅ Esperado: Em oportunidade/detail, vê botão "Deletar"
   - ✅ Pode deletar com confirmação
   - ❌ Se: Botão não aparece → Template errado!

5. **Acessar `/clientes/`**
   - ✅ Esperado: Vê todos os clientes
   - ✅ Botão "Novo Cliente" deve estar visível

6. **Criar novo cliente**
   - ✅ Esperado: Pode criar novo cliente
   - ❌ Se: Erro 403 → BUG!

7. **Acessar `/relatorios/`**
   - ✅ Esperado: Vê página de relatórios com dados
   - ❌ Se: Erro 403 → Decorador muito restritivo!

8. **Tentar acessar `/gerenciar/painel/` (admin panel)**
   - ✅ Esperado: Erro 403 (Forbidden)
   - ❌ Se: Acessa painel → BUG DE SEGURANÇA!

---

## 🧪 Teste 4: ADMIN (Acesso total)

### Login como superuser/admin

1. **Todas as URLs funcionam normalmente**
   - ✅ Acesso total a tudo
   - ✅ Botões "Nova", "Editar", "Deletar" todos visíveis
   - ✅ Admin panel `/gerenciar/painel/` acessível

2. **Pode acessar `/gerenciar/usuarios/`**
   - ✅ Lista de usuários com filtros
   - ✅ Pode editar roles
   - ✅ Pode deletar usuários

3. **Pode ver `/relatorios/`**
   - ✅ Com todas as métricas

---

## 🧪 Teste 5: SEGURANÇA - Tentativas de Bypass

### Verificar se sistema resiste a bypass

1. **Visitante tenta acessar URL direta**
   ```
   GET /oportunidades/1/editar/
   ✅ Esperado: 403 Forbidden
   ❌ Se: Carrega → Falta decorador na view!
   ```

2. **Analista tenta POST para criar oportunidade**
   ```
   POST /oportunidades/criar/
   ✅ Esperado: 403 Forbidden
   ❌ Se: Cria → @role_required não está bloqueando!
   ```

3. **Visitante tenta acessar admin panel**
   ```
   GET /gerenciar/painel/
   ✅ Esperado: 403 Forbidden
   ❌ Se: Acessa → @admin_required não está funcionando!
   ```

4. **Testar cookie/session manipulation**
   ```
   Copiar cookie de outro usuário e colar
   ✅ Esperado: Django session invalidada
   ❌ Se: Funciona com outro perfil → CRÍTICO!
   ```

---

## ✅ Checklist de Testes

### Visitante ✅
- [ ] Bloqueado de `/oportunidades/`
- [ ] Bloqueado de `/clientes/`
- [ ] Bloqueado de `/atividades/`
- [ ] Bloqueado de `/relatorios/`
- [ ] Menu vazio (exceto Dashboard)

### Analista ✅
- [ ] Vê suas oportunidades
- [ ] NÃO vê botão "Nova Oportunidade"
- [ ] NÃO vê botão "Editar"
- [ ] NÃO vê botão "Deletar"
- [ ] Vê `/clientes/` (sem criar)
- [ ] Vê `/relatorios/`
- [ ] Bloqueado de `/gerenciar/painel/`

### Gerente ✅
- [ ] Vê suas oportunidades
- [ ] VÊ botão "Nova Oportunidade"
- [ ] Pode criar oportunidades
- [ ] Pode editar suas oportunidades
- [ ] Pode deletar suas oportunidades
- [ ] Vê todos os clientes
- [ ] Pode criar clientes
- [ ] Vê `/relatorios/`
- [ ] Bloqueado de `/gerenciar/painel/`

### Admin ✅
- [ ] Acesso total a tudo
- [ ] Vê todas as oportunidades
- [ ] Acesso a `/gerenciar/painel/`
- [ ] Pode criar/editar/deletar usuários
- [ ] Vê `/relatorios/`

---

## 🚨 Problemas Conhecidos Esperados

Se encontrar qualquer um destes, é BUG:

1. ❌ Visitante vê oportunidades
2. ❌ Analista pode criar oportunidade
3. ❌ Analista pode deletar oportunidade
4. ❌ Visitante acessa admin panel
5. ❌ Analista vê botão "Editar"
6. ❌ Gerente vê TODAS oportunidades (não filtradas)
7. ❌ Formulário acessível mesmo com 403

---

## 📝 Relatório de Testes

Após completar todos os testes, preencha:

```
Data: __/__/____
Testador: ___________

VISITANTE: ✅ Passou / ❌ Falhou
Problemas: ____________________

ANALISTA: ✅ Passou / ❌ Falhou
Problemas: ____________________

GERENTE: ✅ Passou / ❌ Falhou
Problemas: ____________________

ADMIN: ✅ Passou / ❌ Falhou
Problemas: ____________________

SEGURANÇA: ✅ Passou / ❌ Falhou
Problemas: ____________________

GERAL: ✅ PRONTO / ❌ PRECISA CORREÇÃO
```

---

## 💡 Dicas de Teste

- Use **DevTools** (F12) para ver requisições HTTP
- Verifique **Network** para ver status 403/302
- Use **Console** para ver mensagens de erro
- Teste em **diferentes navegadores** (Chrome, Firefox, Safari)
- Teste em **mobile** (responsive)
- Teste com **VPN desligada** (se aplicável)

---

**Total de Testes:** 50+  
**Tempo Estimado:** 30-45 minutos  
**Criticidade:** ALTA - Sistema de segurança

Boa sorte nos testes! 🚀
