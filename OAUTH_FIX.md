# 🔧 SOLUÇÃO RÁPIDA - Erro de Autenticação OAuth

## ❌ Erro Atual
```
Ocorreu um erro ao conectar com a rede social
Desculpe, houve um problema ao tentar autenticá-lo.
```

---

## ✅ Solução em 3 passos

### Passo 1: Copiar credenciais do Google Cloud Console

Na tela que você mandou, pega:
- **Client ID**: `xxxxxx.apps.googleusercontent.com`
- **Secret**: (a chave secreta)

### Passo 2: Configurar no Django

```bash
cd /home/marcus/desenvolvimento/Outlook

# Opção A: Via comando (mais fácil)
uv run manage.py setup_oauth \
  --client-id=SEU_CLIENT_ID \
  --secret=SEU_SECRET \
  --domain=localhost:8555

# Opção B: Interativo (será pedido durante execução)
uv run manage.py setup_oauth
```

### Passo 3: Reiniciar servidor

```bash
pkill -f "runserver"
cd /home/marcus/desenvolvimento/Outlook
uv run manage.py runserver 8555
```

---

## 🔍 Verificar Configuração

Se quiser ver o status:

```bash
# Admin (acesso restrito)
http://localhost:8555/oauth-status/
```

Ou via Django Shell:

```bash
uv run manage.py shell

# Digite:
from allauth.socialaccount.models import SocialApp
for app in SocialApp.objects.all():
    print(f"{app.provider}: {app.client_id[:20]}...")
    
# Sair: exit()
```

---

## 🚨 Possível Causa do Erro

O app Google **não estava configurado** no banco de dados do Django. O comando `setup_oauth` cria automaticamente.

---

## 🎯 Próximas Tentativas

1. Certifique-se que o **domínio da URI de redirect** no Google Cloud corresponde
2. Se tiver usando `127.0.0.1:8555` em vez de `localhost:8555`, ajuste:
   ```bash
   uv run manage.py setup_oauth --domain=127.0.0.1:8555
   ```

3. Se ainda não funcionar, verifique logs:
   ```bash
   # Terminal com servidor rodando mostrará erros detalhados
   ```

---

## 📞 Support

Se persistir o erro, execute com verbose:

```bash
uv run manage.py runserver 8555 --verbosity 3
```

E compartilhe os logs aqui!

