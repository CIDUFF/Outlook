import threading

# Armazenar o usuário atual da thread
_thread_locals = threading.local()


def get_current_user():
    """Obtém o usuário atual da thread"""
    return getattr(_thread_locals, 'user', None)


def set_current_user(user):
    """Define o usuário atual da thread"""
    _thread_locals.user = user


class AuditMiddleware:
    """Middleware para capturar o usuário atual em requisições"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Capturar o usuário da requisição
        if request.user and request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)
        
        response = self.get_response(request)
        return response
