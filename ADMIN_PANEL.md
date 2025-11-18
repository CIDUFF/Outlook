# 📊 Painel de Administração - PROSPECTA

## Visão Geral

O painel de administração do PROSPECTA fornece controle completo sobre gerenciamento de usuários, papéis e permissões através de uma interface intuitiva com Tailwind CSS.

## 🎯 Funcionalidades

### Dashboard Administrativo
- **Visão Geral**: Estatísticas em tempo real de usuários, admins, gerentes, vendedores, analistas e inativos
- **Cards Informativos**: Exibição visual de contadores com ícones coloridos
- **Atalhos Rápidos**: Acesso direto para gerenciar usuários e criar novos usuários

### Gerenciamento de Usuários

#### Listar Usuários
- **Busca e Filtros**:
  - Pesquisa por nome ou email
  - Filtro por papel (admin, gerente, vendedor, analista)
  - Filtro por status (ativo/inativo)
- **Visualização em Tabela**:
  - Nome completo
  - Email
  - Papel (com badges coloridas)
  - Status (com badges coloridas)
  - Ações rápidas (editar, deletar)

#### Editar Usuário
- Atualizar nome completo (nome e sobrenome)
- Atualizar email
- Modificar papel/função
- Definir departamento
- Registrar telefone
- Ativar/desativar usuário
- Sincronização automática de privilégios de staff com papel de admin

#### Criar Novo Usuário
- Campos obrigatórios: usuário, email, primeiro nome, senha
- Campos opcionais: sobrenome, departamento, telefone
- Validação de unicidade: verifica se usuário/email já existem
- Atribuição de papel no momento da criação
- Descrição de cada papel para orientação

#### Deletar Usuário
- Confirmação de segurança para evitar deleções acidentais
- Exibição de informações do usuário a ser deletado
- Aviso sobre dados associados serem permanentemente removidos
- Deleção em cascata de perfil associado

## 🔐 Controle de Acesso

### Decorator @admin_required
```python
@login_required(login_url='account_login')
@admin_required
def admin_view(request):
    # Apenas superuser ou usuários com role 'admin' acessam
    pass
```

**Verificações**:
1. Usuário autenticado
2. Superuser OU profile.is_admin() (role == 'admin')
3. Redirecionamento com mensagem de erro se não atender critérios

## 📍 Rotas de URL

| URL | Função | Nome |
|-----|--------|------|
| `/admin/painel/` | Dashboard | `admin_dashboard` |
| `/admin/usuarios/` | Listar usuários | `admin_users_list` |
| `/admin/usuarios/criar/` | Criar usuário | `admin_create_user` |
| `/admin/usuarios/<id>/` | Editar usuário | `admin_user_detail` |
| `/admin/usuarios/<id>/deletar/` | Deletar usuário | `admin_user_delete` |
| `/admin/usuarios/<id>/toggle-status/` | Ativar/Desativar (AJAX) | `admin_user_toggle_status` |

## 🎨 Templates

Todos os templates estão em `prospecta/templates/prospecta/admin/`:

- **dashboard.html** - Painel principal com estatísticas
- **users_list.html** - Lista de usuários com filtros
- **user_detail.html** - Edição de usuário
- **user_delete_confirm.html** - Confirmação de deleção
- **user_create.html** - Criação de novo usuário

### Estilos
- Framework: **Tailwind CSS** (via CDN)
- Cores: Azul, verde, vermelho, roxo, amarelo para diferentes estados
- Responsivo: Funciona em desktop, tablet e mobile
- Ícones: Font Awesome integrado

## 📝 Fluxo de Negócio

### Criar Novo Usuário
1. Navegar para `/admin/usuarios/criar/`
2. Preencher formulário com dados obrigatórios
3. Sistema valida unicidade de usuário/email
4. Cria instância de User com password hash
5. Cria UserProfile associado com papel selecionado
6. Se papel = 'admin', marca como `is_staff = True`
7. Redireciona para lista com mensagem de sucesso

### Editar Usuário
1. Navegar para `/admin/usuarios/<id>/`
2. Modificar campos necessários
3. Sistema salva User e UserProfile
4. Se papel mudou para admin, atualiza `is_staff`
5. Se papel mudou de admin, remove `is_staff`
6. Redireciona com feedback de sucesso

### Deletar Usuário
1. Navegar para `/admin/usuarios/<id>/deletar/`
2. Confirmação com informações do usuário
3. POST confirma deleção
4. Django deleta User (UserProfile deletado em cascata via ForeignKey)
5. Redireciona para lista com mensagem de sucesso

## 🔗 Integração com Modelos

### UserProfile
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('vendedor', 'Vendedor'),
        ('analista', 'Analista'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='vendedor')
    is_active = models.BooleanField(default=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def is_admin(self):
        return self.role == 'admin'
```

## ⚙️ Variáveis de Contexto

Todas as views passam:
- `page_title` - Título da página
- `total_users` - Total de usuários (dashboard)
- Filtros e resultados (listar usuarios)
- `role_choices` - Opções de papel

## 🚀 Próximos Passos

1. Adicionar autolog para auditoria de ações admin
2. Exportar lista de usuários em CSV/Excel
3. Gerenciamento de permissões mais granular
4. Histórico de alterações por usuário
5. Notificações quando novo usuário é criado
6. Backup e restauração de dados

## 📱 Suporte

Para problemas com o painel admin:
- Verificar se usuário está autenticado e é admin
- Confirmar UserProfile está criado para o usuário
- Validar permissões no decorator @admin_required
- Verificar logs de erro no Django
