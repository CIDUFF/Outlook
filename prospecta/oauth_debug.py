"""
Debug utilities para OAuth
"""
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger('prospecta.oauth')
logger.setLevel(logging.DEBUG)

# Criar file handler
fh = logging.FileHandler('/tmp/oauth_debug.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def log_oauth_error(request, exception, extra_info=None):
    """Log de erros OAuth"""
    logger.error(f"OAuth Error occurred", extra={
        'exception': str(exception),
        'exception_type': type(exception).__name__,
        'request_method': request.method,
        'request_path': request.path,
        'get_params': dict(request.GET.items()),
        'extra_info': extra_info
    })


def get_oauth_debug_info():
    """Get debug info from OAuth"""
    try:
        with open('/tmp/oauth_debug.log', 'r') as f:
            return f.read()
    except:
        return "No log file found"
