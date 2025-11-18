"""
Custom allauth adapters para conexão de contas sociais com usuários existentes.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter customizado que conecta contas sociais a usuários existentes
    pelo email, evitando duplicação de usuários.
    """

    def pre_social_login(self, request, sociallogin):
        """
        Se o email do social login já existe na base, conecta à conta existente
        em vez de criar uma nova.
        """
        if sociallogin.is_existing:
            return

        try:
            email = sociallogin.account.extra_data.get('email', '')
            if not email:
                return

            # Procura usuário existente com o mesmo email
            existing_user = User.objects.get(email=email)

            # Conecta o social account ao usuário existente
            sociallogin.connect(request, existing_user)

        except User.DoesNotExist:
            # Se não existe, deixa o allauth criar normalmente
            pass
        except Exception as e:
            # Log de erros mas não bloqueia o fluxo
            print(f"Erro ao conectar social account: {e}")
            pass
