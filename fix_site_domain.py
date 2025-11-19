#!/usr/bin/env python
"""
Script para corrigir o domain/site do Django para OAuth funcionar corretamente.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Outlook.settings')
django.setup()

from django.contrib.sites.models import Site

def fix_site_domain():
    """Corrige o domain do site para o domínio correto"""
    site_id = 1
    correct_domain = 'prospecta.cid-uff.net'
    correct_name = 'PROSPECTA - CID-UFF'
    
    try:
        site = Site.objects.get(pk=site_id)
        old_domain = site.domain
        old_name = site.name
        
        site.domain = correct_domain
        site.name = correct_name
        site.save()
        
        print(f"✅ Site atualizado com sucesso!")
        print(f"   ID: {site_id}")
        print(f"   Domain: {old_domain} → {correct_domain}")
        print(f"   Name: {old_name} → {correct_name}")
        print(f"\n📝 Agora certifique-se que no Google Cloud Console você tem:")
        print(f"   • URIs de redirecionamento autorizados:")
        print(f"     - https://{correct_domain}/accounts/google/login/callback/")
        print(f"   • Origens JavaScript autorizadas:")
        print(f"     - https://{correct_domain}")
        
    except Site.DoesNotExist:
        site = Site.objects.create(
            pk=site_id,
            domain=correct_domain,
            name=correct_name
        )
        print(f"✅ Site criado com sucesso!")
        print(f"   Domain: {correct_domain}")
        print(f"   Name: {correct_name}")

if __name__ == '__main__':
    fix_site_domain()
