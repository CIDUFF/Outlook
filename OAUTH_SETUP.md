# Guia: Adicionar Login com Google no PROSPECTA

## Passo 1: Criar um Projeto no Google Cloud Console

1. Acesse https://console.cloud.google.com/
2. Faça login com sua conta Google
3. Clique no menu dropdown de projetos no topo
4. Clique em "NEW PROJECT"
5. Digite um nome (ex: "PROSPECTA OAuth")
6. Clique em "CREATE"

## Passo 2: Ativar a API Google+

1. No console, procure por "APIs & Services"
2. Clique em "Enable APIs and Services"
3. Procure por "Google+ API" 
4. Selecione e clique em "ENABLE"

## Passo 3: Criar as Credenciais OAuth

1. Vá para "Credentials" no menu esquerdo
2. Clique em "Create Credentials" → "OAuth 2.0 Client ID"
3. Se pedido, configure a "OAuth consent screen" primeiro:
   - Escolha "External" como tipo de usuário
   - Preencha informações básicas:
     - **App name**: PROSPECTA
     - **User support email**: seu@email.com
     - **Developer contact**: seu@email.com
   - Clique em "Save and Continue"
4. Volte para criar Client ID
5. Selecione "Web application"
6. Dê um nome (ex: "PROSPECTA Local")
7. Em "Authorized redirect URIs" adicione:
   ```
   http://127.0.0.1:8555/accounts/google/login/callback/
   http://localhost:8555/accounts/google/login/callback/
   ```
8. Clique em "CREATE"

## Passo 4: Copiar as Credenciais

Após criar, você verá uma janela com:
- **Client ID**: (copie este)
- **Client Secret**: (copie este)

Guarde esses valores!

## Passo 5: Configurar no Django Admin

1. Inicie o servidor: `uv run manage.py runserver 8555`
2. Acesse: http://localhost:8555/admin/
3. Faça login com superuser (ou crie um: `uv run manage.py createsuperuser`)
4. Vá para "Sites" no admin
   - Certifique-se de que existe um site com domain "127.0.0.1:8555"
   - Se não existir, crie um
5. Vá para "Social Applications" (em django-allauth)
6. Clique em "Add Social Application"
7. Preencha:
   - **Provider**: Google
   - **Name**: Google OAuth
   - **Client id**: (Cole o Client ID do passo 4)
   - **Secret key**: (Cole o Client Secret do passo 4)
   - **Sites**: Selecione o seu site
8. Clique em "Save"

## Passo 6: Testar

1. Acesse http://localhost:8555/accounts/login/
2. Clique no botão "Google"
3. Você será redirecionado para o Google
4. Após autorizar, será criada uma conta no PROSPECTA

## Notas Importantes

- O domínio precisa ser exatamente igual nas URLs de callback
- Para produção, mude a URL para seu domínio real (ex: `https://meusite.com/accounts/google/login/callback/`)
- Em produção, use `HTTPS` sempre

## Troubleshooting

Se receber erro "redirect_uri_mismatch":
- Verifique se a URL no Admin Social Applications bate com a que o Google espera
- Certifique-se de que o Site no Admin está configurado corretamente

Se o login não aparecer:
- Verifique que a SocialApp foi criada no Admin
- Confirme que o Provider está como "Google"
- Reinicie o servidor
