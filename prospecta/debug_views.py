"""
Views para debugar OAuth
"""
import logging
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@require_http_methods(['GET'])
def oauth_debug(request):
    """View para ver logs de OAuth"""
    if not request.user.is_superuser:
        return HttpResponse("Forbidden", status=403)
    
    try:
        with open('/tmp/django_oauth.log', 'r') as f:
            logs = f.read()
    except:
        logs = "Log file not found"
    
    html = f"""
    <html>
    <head><title>OAuth Debug</title></head>
    <body style="font-family: monospace; white-space: pre-wrap; padding: 20px;">
    <h1>OAuth Debug Logs</h1>
    <hr>
    {logs}
    </body>
    </html>
    """
    return HttpResponse(html)
