"""
Temporary debug view for OAuth errors
"""
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from prospecta.oauth_debug import get_oauth_debug_info


@require_http_methods(['GET'])
def oauth_debug_log(request):
    """View para ver logs de OAuth debug"""
    if not request.user.is_superuser:
        return HttpResponse("Forbidden", status=403)
    
    logs = get_oauth_debug_info()
    return HttpResponse(f"<pre>{logs}</pre>", content_type="text/html")
