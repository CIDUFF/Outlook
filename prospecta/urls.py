from django.urls import path
from . import views
from . import admin_views
from . import calendar_views

app_name = 'prospecta'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),

    # Dashboard and main views (require login)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.profile_view, name='profile'),

    # Admin panel
    path('gerenciar/painel/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('gerenciar/usuarios/', admin_views.admin_users_list,
         name='admin_users_list'),
    path('gerenciar/usuarios/criar/', admin_views.admin_create_user,
         name='admin_create_user'),
    path('gerenciar/usuarios/<int:user_id>/',
         admin_views.admin_user_detail, name='admin_user_detail'),
    path('gerenciar/usuarios/<int:user_id>/deletar/',
         admin_views.admin_user_delete, name='admin_user_delete'),
    path('gerenciar/usuarios/<int:user_id>/toggle-status/',
         admin_views.admin_user_toggle_status, name='admin_user_toggle_status'),
    path('gerenciar/permissoes/',
         admin_views.permissions_matrix, name='permissions_matrix'),
    path('gerenciar/ajuda/',
         admin_views.admin_help, name='admin_help'),

    # Opportunities
    path('oportunidades/', views.opportunities_list, name='opportunities_list'),
    path('oportunidades/criar/', views.opportunity_create,
         name='opportunity_create'),
    path('oportunidades/<uuid:pk>/',
         views.opportunity_detail, name='opportunity_detail'),
    path('oportunidades/<uuid:pk>/editar/',
         views.opportunity_update, name='opportunity_update'),
    path('oportunidades/<uuid:pk>/deletar/',
         views.opportunity_delete, name='opportunity_delete'),
    path('oportunidades/<uuid:pk>/adicionar-participante/',
         views.add_opportunity_participant, name='add_opportunity_participant'),
    path('oportunidades/<uuid:pk>/remover-participante/<uuid:participant_id>/',
         views.remove_opportunity_participant, name='remove_opportunity_participant'),
    path('oportunidades/<uuid:pk>/notificacoes-participante/<uuid:participant_id>/',
         views.toggle_participant_notifications, name='toggle_participant_notifications'),

    # HTMX endpoints for opportunities
    path('api/oportunidades/filtrar/',
         views.opportunities_filter, name='opportunities_filter'),
    path('api/oportunidades/<uuid:pk>/status/',
         views.opportunity_status_update, name='opportunity_status_update'),

    # Clients
    path('clientes/', views.clients_list, name='clients_list'),
    path('clientes/criar/', views.client_create, name='client_create'),
    path('clientes/<uuid:pk>/', views.client_detail, name='client_detail'),
    path('clientes/<uuid:pk>/editar/', views.client_update, name='client_update'),

    # Activities
    path('atividades/', views.activities_list, name='activities_list'),
    path('atividades/<uuid:pk>/aprovar/',
         views.activity_approve, name='activity_approve'),
    path('atividades/criar/<uuid:stage_pk>/',
         views.activity_create, name='activity_create'),
    path('atividades/<uuid:pk>/editar/',
         views.activity_update, name='activity_update'),
    path('atividades/<uuid:pk>/deletar/',
         views.activity_delete, name='activity_delete'),

    # Stages
    path('etapas/', views.stages_list, name='stages_list'),
    path('etapas/criar/<uuid:opportunity_pk>/',
         views.stage_create, name='stage_create'),
    path('etapas/<uuid:pk>/editar/',
         views.stage_update, name='stage_update'),
    path('etapas/<uuid:pk>/deletar/',
         views.stage_delete, name='stage_delete'),

    # Contacts
    path('contatos/', views.contacts_list, name='contacts_list'),
    path('contatos/criar/<uuid:client_pk>/',
         views.contact_create, name='contact_create'),
    path('contatos/<uuid:pk>/editar/',
         views.contact_update, name='contact_update'),
    path('contatos/<uuid:pk>/deletar/',
         views.contact_delete, name='contact_delete'),

    # Sales Models
    path('modelos-venda/', views.sales_model_list, name='sales_model_list'),
    path('modelos-venda/criar/', views.sales_model_create,
         name='sales_model_create'),
    path('modelos-venda/<uuid:pk>/editar/',
         views.sales_model_update, name='sales_model_update'),
    path('modelos-venda/<uuid:pk>/deletar/',
         views.sales_model_delete, name='sales_model_delete'),

    # Reports and dashboards
    path('relatorios/', views.reports, name='reports'),

    # Search
    path('buscar/', views.search_global, name='search_global'),

    # ========================================================================
    # DOCUMENTOS E ANEXOS
    # ========================================================================
    path('oportunidades/<uuid:pk>/documentos/',
         calendar_views.opportunity_documents, name='opportunity_documents'),
    path('oportunidades/<uuid:pk>/documentos/upload/',
         calendar_views.upload_opportunity_document, name='upload_opportunity_document'),
    path('documentos/<uuid:pk>/deletar/',
         calendar_views.delete_opportunity_document, name='delete_opportunity_document'),

    path('atividades/<uuid:pk>/anexos/upload/',
         calendar_views.upload_activity_attachment, name='upload_activity_attachment'),
    path('anexos/<uuid:pk>/deletar/',
         calendar_views.delete_activity_attachment, name='delete_activity_attachment'),

    # ========================================================================
    # REUNIÕES E CALENDÁRIO
    # ========================================================================
    path('oportunidades/<uuid:pk>/reunioes/',
         calendar_views.opportunity_meetings, name='opportunity_meetings'),
    path('oportunidades/<uuid:pk>/reunioes/criar/',
         calendar_views.create_meeting, name='create_meeting'),
    path('reunioes/<uuid:pk>/editar/',
         calendar_views.edit_meeting, name='edit_meeting'),
    path('reunioes/<uuid:pk>/deletar/',
         calendar_views.delete_meeting, name='delete_meeting'),
    path('atividades/<uuid:activity_pk>/associar-reuniao/',
         calendar_views.associate_meeting_to_activity, name='associate_meeting_to_activity'),
    path('atividades/<uuid:activity_pk>/associar-reuniao-rapido/',
         calendar_views.activity_quick_associate, name='activity_quick_associate'),
]
