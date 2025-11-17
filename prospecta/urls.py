from django.urls import path
from . import views
from . import debug_views

app_name = 'prospecta'

urlpatterns = [
    # Debug URLs
    path('debug/oauth/', debug_views.oauth_debug, name='oauth_debug'),
    
    # Public pages
    path('', views.home, name='home'),
    
    # Dashboard and main views (require login)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.profile_view, name='profile'),
    
    # Google OAuth
    path('auth/google/', views.google_oauth_login, name='google_oauth_login'),
    
    # Opportunities
    path('oportunidades/', views.opportunities_list, name='opportunities_list'),
    path('oportunidades/criar/', views.opportunity_create, name='opportunity_create'),
    path('oportunidades/<uuid:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('oportunidades/<uuid:pk>/editar/', views.opportunity_update, name='opportunity_update'),
    path('oportunidades/<uuid:pk>/deletar/', views.opportunity_delete, name='opportunity_delete'),
    
    # HTMX endpoints for opportunities
    path('api/oportunidades/filtrar/', views.opportunities_filter, name='opportunities_filter'),
    path('api/oportunidades/<uuid:pk>/status/', views.opportunity_status_update, name='opportunity_status_update'),
    
    # Clients
    path('clientes/', views.clients_list, name='clients_list'),
    path('clientes/criar/', views.client_create, name='client_create'),
    path('clientes/<uuid:pk>/', views.client_detail, name='client_detail'),
    path('clientes/<uuid:pk>/editar/', views.client_update, name='client_update'),
    
    # Activities
    path('atividades/', views.activities_list, name='activities_list'),
    path('atividades/<uuid:pk>/aprovar/', views.activity_approve, name='activity_approve'),
    
    # Reports and dashboards
    path('relatorios/', views.reports, name='reports'),
]
