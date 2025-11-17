# PROSPECTA - Sistema de Gestão de Oportunidades

Sistema completo de gestão de oportunidades e vendas com autenticação OAuth, desenvolvido com Django 5.2+, HTML5, Tailwind CSS e HTMX.

## 🚀 Funcionalidades Principais

### 1. **Autenticação e Controle de Acesso**
- Autenticação OAuth com Django-allauth (Google, GitHub)
- Sistema de roles baseado em permissões:
  - **Administrador**: Acesso total ao sistema
  - **Gerente de Vendas**: Acesso a gestão de clientes e oportunidades
  - **Vendedor**: Acesso às suas oportunidades e atividades
  - **Analista**: Visualização de clientes e relatórios

### 2. **Gestão de Oportunidades**
- Criar, editar e deletar oportunidades
- Acompanhar status (Aberta, Em Andamento, Ganha, Perdida, Cancelada)
- Atribuir responsáveis
- Histórico completo de mudanças
- Filtros por status, cliente e data
- Atualização de status com HTMX

### 3. **Gestão de Clientes**
- Cadastro completo de clientes com CNPJ
- Gerenciamento de contatos por cliente
- Visualização de todas as oportunidades do cliente
- Busca por nome, CNPJ ou e-mail

### 4. **Controle de Atividades**
- Atribuição de atividades aos usuários
- Sistema de aprovação para atividades
- Acompanhamento de status
- Controle de datas esperadas vs. realizadas

### 5. **Relatórios e Análises**
- Pipeline de vendas
- Taxa de conversão
- Ticket médio
- Distribuição de oportunidades por status
- Valor total ganho/perdido

### 6. **Dashboard Inteligente**
- Visualização de dados específicos por role
- Widgets interativos
- Oportunidades recentes
- Atividades pendentes
- Estatísticas em tempo real

## 📋 Requisitos

- Python 3.12+
- PostgreSQL 12+
- Node.js (para Tailwind CSS - opcional)

## 🔧 Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd Outlook
```

### 2. Configure o ambiente

```bash
# Criar ambiente virtual com uv (recomendado)
uv venv

# Ativar ambiente virtual
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
uv sync
```

### 4. Configure o banco de dados

```bash
# Edite o arquivo settings.py com suas credenciais PostgreSQL
```

### 5. Execute as migrations

```bash
uv run manage.py makemigrations
uv run manage.py migrate
```

### 6. Crie um usuário admin

```bash
uv run manage.py createsuperuser
```

### 7. Inicie o servidor

```bash
uv run manage.py runserver 8555
```

Acesse: http://localhost:8555

## 📁 Estrutura do Projeto

```
Outlook/
├── manage.py
├── pyproject.toml
├── Outlook/
│   ├── settings.py          # Configurações do Django
│   ├── urls.py              # URLs principais
│   ├── wsgi.py
│   └── asgi.py
└── prospecta/
    ├── models.py            # Modelos de dados
    ├── views.py             # Lógica de negócio
    ├── urls.py              # URLs da aplicação
    ├── admin.py             # Configuração do admin
    ├── middleware.py        # Middlewares customizados
    ├── templates/
    │   └── prospecta/
    │       ├── base.html                    # Template base
    │       ├── home.html                    # Página inicial
    │       ├── dashboard.html               # Dashboard
    │       ├── profile.html                 # Perfil do usuário
    │       ├── reports.html                 # Relatórios
    │       ├── opportunities/
    │       │   ├── list.html                # Lista de oportunidades
    │       │   ├── form.html                # Formulário
    │       │   └── detail.html              # Detalhes
    │       ├── clients/
    │       │   ├── list.html                # Lista de clientes
    │       │   ├── form.html                # Formulário
    │       │   └── detail.html              # Detalhes
    │       ├── activities/
    │       │   └── list.html                # Lista de atividades
    │       └── components/                  # Componentes HTMX
    ├── migrations/          # Migrations do banco
    └── static/              # Arquivos estáticos
```

## 🗄️ Modelos de Dados

### UserProfile
Estende o modelo User do Django com roles e permissões
- **role**: admin, gerente, vendedor, analista
- **department**: Departamento do usuário
- **avatar**: Foto de perfil
- **phone**: Telefone

### Client
Dados dos clientes
- **name**: Nome da empresa
- **cnpj**: CNPJ único
- **email**: E-mail corporativo
- **address**: Endereço completo

### Contact
Contatos dos clientes
- **name**: Nome do contato
- **email**: E-mail pessoal
- **phone**: Telefone
- **position**: Cargo

### Opportunity
Oportunidades de venda
- **title**: Título da oportunidade
- **client**: Cliente relacionado
- **status**: Status da oportunidade
- **value_brl**: Valor em reais
- **responsible_user**: Responsável

### Stage e Activity
Etapas e atividades dentro de uma oportunidade
- Acompanhamento do progresso
- Histórico de mudanças
- Status de aprovação

## 🔐 Autenticação OAuth

### Configurar Google OAuth

1. Acesse Google Cloud Console
2. Crie um novo projeto
3. Ative a API Google+ 
4. Crie credenciais (OAuth 2.0)
5. Configure URLs de redirecionamento
6. Adicione client_id e client_secret em `/admin/socialaccount/socialapp/`

### Configurar GitHub OAuth

1. Acesse GitHub Settings > Developer settings
2. Crie uma nova OAuth App
3. Configure Authorization callback URL
4. Adicione client_id e client_secret em `/admin/socialaccount/socialapp/`

## 🎨 Tecnologias Utilizadas

- **Backend**: Django 5.2+
- **Frontend**: HTML5, Tailwind CSS, HTMX
- **Autenticação**: django-allauth, social-auth
- **Banco**: PostgreSQL
- **ORM**: Django ORM
- **Admin**: Django Admin

## 📊 Fluxo de Negócio

### Criação de Oportunidade
1. Vendedor cria nova oportunidade
2. Associa cliente existente ou cria novo
3. Define etapas do processo
4. Cria atividades relacionadas
5. Histórico é registrado automaticamente

### Acompanhamento
1. Todos os usuários podem acompanhar suas oportunidades
2. Atualizar status em tempo real com HTMX
3. Delegar atividades para equipe
4. Visualizar histórico de mudanças

### Aprovação
1. Gerente/Admin aprova atividades
2. Marca como concluída
3. Libera próximas etapas
4. Gera dados para relatórios

## 🛠️ Customização

### Adicionar novo role

Edite `prospecta/models.py` em `UserProfile.ROLE_CHOICES`:

```python
ROLE_CHOICES = [
    ('novo_role', 'Descrição'),
    # ...
]
```

### Adicionar nova etapa

Use o Django Admin para criar Stage ou através de views.

### Customizar templates

Os templates estão em `prospecta/templates/` e usam Django template syntax com Tailwind.

## 📱 Responsividade

Todos os templates são 100% responsivos para:
- Desktop (1920px+)
- Tablet (768px - 1024px)
- Mobile (< 768px)

## ⚡ Performance

- HTMX para requisições assíncronas sem recarregar página
- Paginação implementada
- Índices no banco de dados
- Cache de templates Django

## 🔒 Segurança

- CSRF protection ativado
- SQL Injection prevention via ORM
- XSS protection via template escaping
- Autenticação obrigatória em views críticas
- Permissões por role em todas as operações

## 📝 API Endpoints

### Oportunidades
- `GET /oportunidades/` - Listar
- `POST /oportunidades/criar/` - Criar
- `GET /oportunidades/<id>/` - Detalhes
- `POST /oportunidades/<id>/editar/` - Atualizar
- `POST /oportunidades/<id>/deletar/` - Deletar
- `POST /api/oportunidades/<id>/status/` - Atualizar status (HTMX)

### Clientes
- `GET /clientes/` - Listar
- `POST /clientes/criar/` - Criar
- `GET /clientes/<id>/` - Detalhes
- `POST /clientes/<id>/editar/` - Atualizar

### Atividades
- `GET /atividades/` - Listar
- `POST /atividades/<id>/aprovar/` - Aprovar

## 🐛 Troubleshooting

### Erro de conexão com banco
Verifique credenciais em `settings.py` e se PostgreSQL está ativo

### HTMX não funciona
Verifique se a biblioteca HTMX está carregando em base.html

### Estilos Tailwind não aparecem
Execute `uv run manage.py collectstatic` e reinicie o servidor

## 📞 Suporte

Para problemas ou sugestões, abra uma issue no repositório.

## 📄 Licença

Propriedade intelectual da NextMarte - 2025

## 👥 Desenvolvimento

- Sistema criado com ❤️ para gestão eficiente de vendas
- Desenvolvido por: Equipe de Desenvolvimento
- Última atualização: 17 de Novembro de 2025
