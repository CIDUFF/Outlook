"""Debug view para OAuth"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.sites.models import Site
from django.conf import settings


@require_http_methods(['GET'])
def oauth_status(request):
    """Verificar status de configuração OAuth"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    try:
        from allauth.socialaccount.models import SocialApp

        site = Site.objects.get_current()
        apps = SocialApp.objects.all()

        data = {
            'site_id': site.id,
            'site_domain': site.domain,
            'site_name': site.name,
            'debug': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'oauth_apps': []
        }

        for app in apps:
            data['oauth_apps'].append({
                'provider': app.provider,
                'name': app.name,
                'client_id': app.client_id[:10] + '***',
                'sites': [str(s) for s in app.sites.all()]
            })

        return JsonResponse(data, indent=2)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
