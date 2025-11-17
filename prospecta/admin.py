from django.contrib import admin
from .models import (
    Client, Contact, SalesModel, Opportunity, Stage, Activity,
    OpportunityHistory, StageHistory, ActivityHistory
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
    list_display = ('title', 'client', 'status', 'value_brl', 'responsible_user', 'created_at')
    search_fields = ('title', 'client__name')
    list_filter = ('status', 'created_at', 'responsible_user')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('name', 'opportunity', 'order', 'created_at')
    search_fields = ('name', 'opportunity__title')
    list_filter = ('created_at', 'opportunity')
    ordering = ('order',)
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'stage', 'status', 'assigned_to', 'created_at')
    search_fields = ('title', 'assigned_to__username')
    list_filter = ('status', 'created_at', 'approved')
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
