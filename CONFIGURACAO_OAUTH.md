# 🔐 Guia de Configuração OAuth - Google & GitHub

## Erro: redirect_uri_mismatch

### ❌ O que significa?
A URL de retorno do seu app Django não corresponde com a registrada no Google Cloud Console.

---

## ✅ Solução Passo a Passo

### Passo 1: Verificar URL do seu app

O Django está rodando em:
```
http://localhost:8555
```

A URL de callback do allauth é:
```
http://localhost:8555/accounts/google/login/callback/
```

---

### Passo 2: Configurar no Google Cloud Console

1. **Acesse**: https://console.cloud.google.com
2. **Selecione seu projeto**
3. **Vá para**: APIs & Services → Credentials
4. **Selecione sua credencial OAuth 2.0**
5. **Clique em: Authorized redirect URIs**
6. **Adicione exatamente**:
   ```
   http://localhost:8555/accounts/google/login/callback/
   http://localhost:8555/accounts/github/login/callback/
   ```

7. **Salve as alterações**

---

### Passo 3: Copiar credenciais para .env

No Google Cloud:

1. Copie o **Client ID**
2. Copie o **Client Secret**

No arquivo `.env` (raiz do projeto):

```env
# Google OAuth
GOOGLE_CLIENT_ID=sua_client_id_aqui.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=sua_client_secret_aqui

# GitHub OAuth
GITHUB_CLIENT_ID=seu_github_client_id
GITHUB_CLIENT_SECRET=seu_github_client_secret
```

---

### Passo 4: Configurar no Django Admin

1. **Acesse**: http://localhost:8555/admin/
2. **Vá para**: Sites → seu site
3. **Certifique-se de que o domínio é**: `localhost:8555`

4. **Vá para**: Social Applications
5. **Crie uma nova aplicação Google**:
   - **Provider**: Google
   - **Name**: Google OAuth
   - **Client ID**: (cole do .env)
   - **Secret Key**: (cole do .env)
   - **Sites**: Selecione seu site

6. **Crie uma para GitHub**:
   - **Provider**: Github
   - **Name**: GitHub OAuth
   - **Client ID**: (cole do .env)
   - **Secret Key**: (cole do .env)
   - **Sites**: Selecione seu site

---

### Passo 5: Reiniciar o servidor

```bash
pkill -f "runserver"
cd /home/marcus/desenvolvimento/Outlook
uv run manage.py runserver 8555
```

---

## 🔍 Debugging

Se ainda der erro, execute:

```bash
cd /home/marcus/desenvolvimento/Outlook
python manage.py shell

# No shell Python:
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Verificar site
print(Site.objects.all())
# Deve aparecer: localhost:8555

# Verificar apps sociais
print(SocialApp.objects.all())
# Deve aparecer Google e GitHub configurados
```

---

## 🌐 Para Produção

Quando colocar em produção, use:

```env
# .env production
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
SITE_ID=1

# Google OAuth
GOOGLE_CLIENT_ID=novo_client_id_producao
GOOGLE_CLIENT_SECRET=novo_client_secret_producao

# No Google Cloud Console, adicionar:
https://seu-dominio.com/accounts/google/login/callback/
https://www.seu-dominio.com/accounts/google/login/callback/
```

---

## ⚡ Quick Fix Local

Se quiser desabilitar OAuth temporariamente (apenas login/senha):

**Em settings.py**, comente:
```python
# 'allauth.socialaccount.providers.google',
# 'allauth.socialaccount.providers.github',
```

E remova dos AUTHENTICATION_BACKENDS:
```python
# 'social_core.backends.google.GoogleOAuth2',
# 'social_core.backends.github.GithubOAuth2',
```

Depois reinicie o servidor.

---

## 📚 Referências

- [Google OAuth Setup](https://developers.google.com/identity/protocols/oauth2)
- [Django-allauth Docs](https://django-allauth.readthedocs.io/)
- [GitHub OAuth Apps](https://docs.github.com/en/developers/apps/building-oauth-apps)

