from django.contrib import admin
from .models import (
    Client, Contact, SalesModel, Opportunity, Stage, Activity,
    OpportunityHistory, StageHistory, ActivityHistory, UserProfile,
    OpportunityDocument, ActivityAttachment, Meeting
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_active', 'department', 'created_at')
    search_fields = ('user__username', 'user__email', 'department')
    list_filter = ('role', 'is_active', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Usuário', {
            'fields': ('user', 'id', 'created_at', 'updated_at')
        }),
        ('Informações Profissionais', {
            'fields': ('role', 'department', 'phone', 'bio')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Avatar', {
            'fields': ('avatar',)
        }),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'cnpj', 'email', 'created_at')
    search_fields = ('name', 'cnpj', 'email')
    list_filter = ('created_at',)
    readonly_fields = ('id', 'created_at')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at', 'client')
    readonly_fields = ('id', 'created_at')


@admin.register(SalesModel)
class SalesModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    readonly_fields = ('id', 'created_at')


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'produto', 'client', 'status', 'value_brl',
                    'responsible_user', 'created_at')
    search_fields = ('title', 'produto', 'client__name')
    list_filter = ('status', 'created_at', 'responsible_user')
    readonly_fields = ('id', 'created_at', 'updated_at')
    filter_horizontal = ('partnerships',)


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('name', 'opportunity', 'order', 'created_at')
    search_fields = ('name', 'opportunity__title')
    list_filter = ('created_at', 'opportunity')
    ordering = ('order',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'stage', 'activity_type',
                    'status', 'assigned_to', 'created_at')
    search_fields = ('title', 'assigned_to__username')
    list_filter = ('status', 'activity_type', 'created_at', 'approved')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(OpportunityHistory)
class OpportunityHistoryAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'change_type', 'changed_by', 'changed_at')
    search_fields = ('opportunity__title', 'change_type')
    list_filter = ('change_type', 'changed_at')
    readonly_fields = ('id', 'changed_at', 'change_details')
    can_delete = False


@admin.register(StageHistory)
class StageHistoryAdmin(admin.ModelAdmin):
    list_display = ('stage', 'change_type', 'changed_by', 'changed_at')
    search_fields = ('stage__name', 'change_type')
    list_filter = ('change_type', 'changed_at')
    readonly_fields = ('id', 'changed_at', 'change_details')
    can_delete = False


@admin.register(ActivityHistory)
class ActivityHistoryAdmin(admin.ModelAdmin):
    list_display = ('activity', 'change_type', 'changed_by', 'changed_at')
    search_fields = ('activity__title', 'change_type')
    list_filter = ('change_type', 'changed_at')
    readonly_fields = ('id', 'changed_at', 'change_details')
    can_delete = False


# ============================================================================
# DOCUMENTOS E ANEXOS
# ============================================================================

@admin.register(OpportunityDocument)
class OpportunityDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'opportunity', 'document_type',
                    'uploaded_by', 'is_public', 'created_at')
    search_fields = ('title', 'opportunity__title', 'description')
    list_filter = ('document_type', 'is_public', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Informações', {
            'fields': ('title', 'opportunity', 'document_type', 'description')
        }),
        ('Arquivo', {
            'fields': ('file', 'is_public')
        }),
        ('Metadados', {
            'fields': ('uploaded_by', 'id', 'created_at', 'updated_at')
        }),
    )


@admin.register(ActivityAttachment)
class ActivityAttachmentAdmin(admin.ModelAdmin):
    list_display = ('activity', 'uploaded_by', 'created_at')
    search_fields = ('activity__title', 'description')
    list_filter = ('created_at',)
    readonly_fields = ('id', 'created_at')


# ============================================================================
# AGENDA E REUNIÕES
# ============================================================================

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'opportunity', 'meeting_type', 'status',
                    'start_datetime', 'organizer')
    search_fields = ('title', 'opportunity__title', 'description')
    list_filter = ('meeting_type', 'status', 'start_datetime')
    readonly_fields = ('id', 'created_at', 'updated_at')
    filter_horizontal = ('attendees',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'opportunity', 'description', 'meeting_type', 'status')
        }),
        ('Data e Hora', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Participantes', {
            'fields': ('organizer', 'attendees')
        }),
        ('Local/Link', {
            'fields': ('location',)
        }),
        ('Notas', {
            'fields': ('notes', 'action_items')
        }),
        ('Metadados', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
