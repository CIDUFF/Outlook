# Configuração de Variáveis de Ambiente

## Sobre

O PROSPECTA usa variáveis de ambiente para armazenar credenciais sensíveis e configurações específicas do ambiente.

## Arquivos

- **`.env`** - Arquivo com suas credenciais reais (NÃO COMMITAR)
- **`.env.example`** - Template com as variáveis necessárias
- **`.gitignore`** - Garante que `.env` não seja versionado

## Como Configurar

### 1. Copiar o template
```bash
cp .env.example .env
```

### 2. Editar `.env` com suas credenciais

```env
# Django Configuration
DEBUG=True
SECRET_KEY=sua-chave-secreta-real

# Database
DB_USER=prospecta_user
DB_PASSWORD=sua-senha-real

# Email (Gmail)
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app-16-caracteres

# Google OAuth
GOOGLE_CLIENT_ID=seu-id-real
GOOGLE_CLIENT_SECRET=seu-secret-real
```

### 3. Variáveis Disponíveis

#### Django
- `DEBUG` - Modo debug (True/False)
- `SECRET_KEY` - Chave secreta do Django
- `ALLOWED_HOSTS` - Hosts permitidos (separados por vírgula)

#### Database
- `DB_ENGINE` - Engine do banco (postgresql, mysql, sqlite3)
- `DB_NAME` - Nome do banco
- `DB_USER` - Usuário do banco
- `DB_PASSWORD` - Senha do banco
- `DB_HOST` - Host do banco
- `DB_PORT` - Porta do banco

#### Email
- `EMAIL_BACKEND` - Backend de email
- `EMAIL_HOST` - Host SMTP (gmail, sendgrid, etc)
- `EMAIL_PORT` - Porta SMTP
- `EMAIL_USE_TLS` - Usar TLS (True/False)
- `EMAIL_HOST_USER` - Email da conta
- `EMAIL_HOST_PASSWORD` - Senha de app
- `DEFAULT_FROM_EMAIL` - Email padrão

#### OAuth
- `GOOGLE_CLIENT_ID` - Client ID do Google
- `GOOGLE_CLIENT_SECRET` - Client Secret do Google

#### Site
- `SITE_ID` - ID do site (Django Sites)
- `LANGUAGE_CODE` - Idioma padrão
- `TIME_ZONE` - Fuso horário

## Segurança

⚠️ **IMPORTANTE:**
- Nunca commit `.env` no repositório
- `.env` está no `.gitignore` para proteção
- Use senhas de app, não a senha real do Gmail
- Em produção, use gerenciadores de secrets (AWS Secrets Manager, HashiCorp Vault, etc)

## Obter Credenciais

### Gmail App Password
1. Habilitar 2FA na conta Google
2. Ir em: https://myaccount.google.com/apppasswords
3. Selecionar "Mail" e "Windows Computer"
4. Copiar a senha de 16 caracteres

### Google OAuth
1. Ir em: https://console.cloud.google.com
2. Criar novo projeto
3. Configurar OAuth 2.0
4. Copiar Client ID e Client Secret

## Teste

Para verificar se está funcionando:
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)
>>> print(settings.EMAIL_HOST_USER)
```
