# Corrigindo o Erro de Autenticação do Google OAuth

## 🔴 Problema

Ao clicar em "Continuar com Google", a autenticação falha com a mensagem:
```
Houve um problema na autenticação. Por favor, tente fazer login novamente.
Problema de segurança
```

## ✅ Solução

O erro ocorre porque o **redirect_uri no Google Console não corresponde** ao redirect_uri que o Django está enviando.

### Passo 1: Identificar a URL de Callback Esperada

O Django/allauth espera que o Google redirecione para:
```
http://127.0.0.1:8555/accounts/google/login/callback/
```

### Passo 2: Adicionar a URL no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/):
   - URL: https://console.cloud.google.com

2. No menu lateral, clique em **APIs & Services** → **Credentials**

3. Encontre o seu OAuth 2.0 Client ID
   - Procure pelo Client ID que começa com `1004376388758...`
   - Clique nele para abrir os detalhes

4. Na seção **"Authorized redirect URIs"**, clique em **"ADD URI"**

5. Adicione esta URL:
   ```
   http://127.0.0.1:8555/accounts/google/login/callback/
   ```

6. Clique em **"SAVE"**

### Passo 3: Testar a Autenticação

1. Volte para http://127.0.0.1:8555/accounts/login/
2. Clique em "Continuar com Google"
3. Você será redirecionado para o Google
4. Autorize o acesso
5. Você será redirecionado para o PROSPECTA

## ℹ️ Informações Adicionais

- **Client ID**: 1004376388758-4d6kfvr5qcc09cuf4mk19tgg1s4dlc4j.apps.googleusercontent.com
- **Redirect URI no Django**: `/accounts/google/login/callback/`
- **View customizada**: `/auth/google/` (redireciona para o Google OAuth)

## 🔗 URLs Configuradas

| URL | Descrição |
|-----|-----------|
| `/auth/google/` | Inicia o fluxo OAuth com Google |
| `/accounts/google/login/` | View padrão do allauth para Google login |
| `/accounts/google/login/callback/` | Callback onde o Google redireciona após autorização |
| `/accounts/login/` | Página de login principal |
| `/accounts/signup/` | Página de signup |

## 💡 Dicas

- Se você receber um erro de **"Invalid redirect_uri"** depois de fazer as mudanças, aguarde alguns minutos para que a alteração seja propagada no Google
- Se ainda não funcionar, verifique se não há espaços ou caracteres especiais na URL
- O protocolo deve ser `http://` (não `https://`) para localhost

## 🚨 Para Produção

Quando migrar para produção, certifique-se de:

1. Alterar o Site Django em `/admin/sites/site/1/`:
   - Mude o domain de `127.0.0.1:8555` para seu domínio de produção (ex: `app.example.com`)

2. Adicionar o novo redirect_uri no Google Console:
   ```
   https://app.example.com/accounts/google/login/callback/
   ```

3. Usar `https://` em produção
