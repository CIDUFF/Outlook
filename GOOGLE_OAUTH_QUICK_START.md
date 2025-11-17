# 🚀 Como Ativar Login com Google no PROSPECTA

## TL;DR (Resumão)

Você precisa de **3 coisas**:

1. **Criar um projeto no Google Cloud** (5 minutos)
2. **Gerar credenciais OAuth** (5 minutos)
3. **Configurar no Django Admin** (2 minutos)

Total: ~12 minutos! ⏱️

---

## ✅ Passo 1: Criar Projeto no Google Cloud (opcional se já tiver)

Se você já tem um projeto no Google Cloud, pule para o Passo 2.

```
1. https://console.cloud.google.com/ (faça login)
2. Clique em "NEW PROJECT" (canto superior)
3. Nome: "PROSPECTA"
4. Clique em "CREATE"
5. Espere criação (aparece no dropdown de projetos)
```

---

## ✅ Passo 2: Obter Client ID e Client Secret

### 2.1 - Ativar Google+ API

```
1. https://console.cloud.google.com/apis/library
2. Procure: "Google+ API"
3. Clique para abrir
4. Clique em "ENABLE"
```

### 2.2 - Criar OAuth Credentials

```
1. Menu esquerdo → "Credentials"
2. Clique em "Create Credentials" (topo)
3. Escolha "OAuth client ID"
4. Se pedir para configurar OAuth Consent Screen, faça:
   ✓ Type: External
   ✓ App name: PROSPECTA
   ✓ User support email: seu@email.com
   ✓ Developer contact: seu@email.com
   ✓ Volte para Credentials
5. Clique novamente em "OAuth client ID"
6. Application type: "Web application"
7. Name: "PROSPECTA Local"
8. Clique em "+ Add URI" em "Authorized redirect URIs"
9. Cole:
   http://127.0.0.1:8555/accounts/google/login/callback/
10. Clique em "CREATE"
11. Copie:
    - Client ID (aquele número gigante)
    - Client Secret (uma string)
```

**Pronto! Guarde essas duas coisas** 📋

---

## ✅ Passo 3: Configurar no Django

### Opção A: Via Script (mais fácil)

```bash
bash setup_google_oauth.sh "seu_client_id_aqui" "seu_client_secret_aqui"
```

Exemplo:
```bash
bash setup_google_oauth.sh "123456.apps.googleusercontent.com" "GCSQT_abcdef123456"
```

### Opção B: Via Admin (manual)

```
1. Abra http://localhost:8555/admin/
2. Faça login (superuser)
3. Se não tiver user admin:
   uv run manage.py createsuperuser
4. Vá para "Social Applications" (em django-allauth)
5. Clique em "+ Add Social Application"
6. Preencha:
   ✓ Provider: Google
   ✓ Name: Google OAuth
   ✓ Client id: (Cole do Passo 2)
   ✓ Secret key: (Cole do Passo 2)
   ✓ Sites: Selecione 127.0.0.1:8555
7. Clique em "SAVE"
```

---

## ✅ Passo 4: Testar!

```
1. http://localhost:8555/accounts/login/
2. Clique no botão "Google" (embaixo do form)
3. Você será levado para Google
4. Autorize
5. Pronto! 🎉
```

---

## ⚠️ Possíveis Problemas

### ❌ Erro: "redirect_uri_mismatch"

**Solução:** A URL de redirecionamento não bate. Verifique:
- No Google Cloud → Authorized redirect URIs: deve conter `http://127.0.0.1:8555/accounts/google/login/callback/`
- No Django Admin → Site domain: deve ser `127.0.0.1:8555`

### ❌ Erro: "SocialApp matching query does not exist"

**Solução:** SocialApp não foi criada. Faça novamente o Passo 3.

### ❌ Botão do Google não aparece

**Solução:**
- Reinicie o servidor: `pkill -f runserver && uv run manage.py runserver 8555`
- Verifique no Admin se SocialApp foi criada

---

## 🎨 Para Produção

Se você vai usar em produção (domínio real):

1. Gere novos Client ID/Secret com URL real:
   ```
   https://seu-dominio.com/accounts/google/login/callback/
   ```

2. No Django, altere o Site domain para seu domínio real

3. Use HTTPS sempre!

---

## 📚 Documentação

- [django-allauth Google Setup](https://django-allauth.readthedocs.io/en/latest/providers.html#google)
- [Google Cloud OAuth Setup](https://cloud.google.com/docs/authentication)

---

**Dúvidas?** Verifique o arquivo `OAUTH_SETUP.md` para detalhes adicionais.
