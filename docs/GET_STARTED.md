# 🚀 Painel de Administração - Guia de Início Rápido

## ⚡ Acesso Rápido

### 1. **Acessar o Painel**
```
http://localhost:8555/admin/painel/
```

### 2. **Requisitos**
- Estar logado como **superuser** ou usuário com **role = 'admin'**
- UserProfile deve estar criado para o usuário

### 3. **Fluxo Principal**

```
Login → Admin → /admin/painel/ → Gerenciar Usuários → CRUD
```

---

## 📍 Rotas Disponíveis

| Rota | Descrição | Método |
|------|-----------|--------|
| `/admin/painel/` | Dashboard com estatísticas | GET |
| `/admin/usuarios/` | Listar usuários com filtros | GET |
| `/admin/usuarios/criar/` | Criar novo usuário | GET/POST |
| `/admin/usuarios/<id>/` | Editar usuário | GET/POST |
| `/admin/usuarios/<id>/deletar/` | Deletar usuário | GET/POST |
| `/admin/usuarios/<id>/toggle-status/` | Ativar/Desativar | POST/AJAX |

---

## 🎯 Casos de Uso

### **Criar Novo Usuário**
1. Clique em "Novo Usuário" no dashboard
2. Preencha: username, email, nome, sobrenome, senha, papel
3. Clique em "Criar Usuário"
4. Será redirecionado para a lista

### **Editar Usuário**
1. Vá para "Gerenciar Usuários"
2. Procure o usuário (use filtros se necessário)
3. Clique em "Editar"
4. Modifique os campos desejados
5. Clique em "Salvar Alterações"

### **Deletar Usuário**
1. Vá para "Gerenciar Usuários"
2. Clique em "Deletar" na linha do usuário
3. Confirme a deleção
4. O usuário será removido permanentemente

### **Filtrar Usuários**
1. Vá para "Gerenciar Usuários"
2. Use os filtros:
   - **Pesquisar**: Digite nome ou email
   - **Papel**: Selecione admin, gerente, vendedor ou analista
   - **Status**: Ativo ou Inativo
3. Clique em "Filtrar"

---

## 🔐 Controle de Acesso

### Apenas Admin pode:
- ✅ Acessar `/admin/painel/`
- ✅ Criar novo usuário
- ✅ Editar qualquer usuário
- ✅ Deletar usuário
- ✅ Ativar/Desativar usuário
- ✅ Alterar papel de usuários

### Se não for admin:
- ❌ Receberá erro 403 (Não autorizado)
- ❌ Será redirecionado para dashboard
- ❌ Mensagem: "Você não tem permissão para acessar"

---

## 💡 Dicas Úteis

### **Criar Admin**
1. Logar como superuser
2. Ir para `/admin/usuarios/criar/`
3. Preencher dados
4. Selecionar papel = **Admin**
5. Criar → Agora é admin!

### **Papéis Disponíveis**

| Papel | Acesso | Descrição |
|-------|--------|-----------|
| **Admin** | Total | Gerencia todo o sistema e usuários |
| **Gerente** | Alto | Gerencia vendedores e oportunidades |
| **Vendedor** | Médio | Cria e gerencia próprias oportunidades |
| **Analista** | Baixo | Visualiza e analisa dados |

### **Desativar Sem Deletar**
Se quiser manter o histórico:
1. Editar usuário
2. Desmarcar "Usuário Ativo"
3. Salvar

Usuário fica inativo mas não é deletado.

---

## ⚙️ Configurações

### **Sincronização Automática**
- Se `role = 'admin'` → `is_staff = True`
- Se `role ≠ 'admin'` → `is_staff = False`
- Funciona automaticamente ao editar!

### **Validações**
- ✅ Username deve ser único
- ✅ Email deve ser único
- ✅ Email deve ser válido
- ✅ Senha será hashada automaticamente

---

## 🐛 Solução de Problemas

### "Erro 404 - Página não encontrada"
```
Solução: Confirmar que as rotas estão em urls.py
Verificar: prospecta/urls.py tem 6 paths admin
```

### "Erro 403 - Sem permissão"
```
Solução: Logar como admin
1. Logar como superuser (geralmente nome: admin)
2. Ir para /admin/usuarios/
3. Encontrar seu usuário
4. Mudar role para 'admin'
5. Tentar novamente
```

### "Erro 500 - Servidor interno"
```
Solução: Verificar logs
Executar: uv run manage.py check
```

---

## 📚 Documentação Completa

Para detalhes técnicos:
- `ADMIN_PANEL.md` - Documentação técnica
- `ADMIN_SETUP.md` - Guia de implementação
- `ADMIN_QUICK_START.txt` - Visão geral rápida

---

## ✅ Checklist

- [ ] Logado como admin?
- [ ] Consegue acessar `/admin/painel/`?
- [ ] Dashboard exibe 6 cards?
- [ ] Botões funcionam?
- [ ] Consegue criar usuário?
- [ ] Consegue editar usuário?
- [ ] Consegue deletar usuário?

Se todos marcados ✅ → Painel funcionando perfeitamente!

---

## 📞 Suporte

### Rápido
1. Consulte `ADMIN_QUICK_START.txt`
2. Veja seção "Troubleshooting"

### Detalhado
1. Leia `ADMIN_PANEL.md`
2. Ou `ADMIN_SETUP.md`

### Técnico
1. Verifique `prospecta/admin_views.py`
2. Consulte `prospecta/urls.py`
3. Verifique templates em `prospecta/templates/prospecta/admin/`

---

**Status: ✅ PRONTO PARA USAR**

Aproveite seu novo painel de administração! 🎉
