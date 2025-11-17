from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import (
    Opportunity, Stage, Activity,
    OpportunityHistory, StageHistory, ActivityHistory
)
from .middleware import get_current_user
import json

# Armazenar valores anteriores para comparação
_previous_values = {}


@receiver(pre_save, sender=Opportunity)
def track_opportunity_pre_save(sender, instance, **kwargs):
    """Armazena valores anteriores antes de salvar"""
    try:
        obj = sender.objects.get(pk=instance.pk)
        _previous_values[f'opportunity_{instance.pk}'] = {
            'title': obj.title,
            'description': obj.description,
            'status': obj.status,
            'value_brl': str(obj.value_brl) if obj.value_brl else None,
            'responsible_user': obj.responsible_user_id,
            'sales_model': obj.sales_model_id,
            'expected_delivery_date': str(obj.expected_delivery_date) if obj.expected_delivery_date else None,
            'delivery_date': str(obj.delivery_date) if obj.delivery_date else None,
        }
    except sender.DoesNotExist:
        pass


@receiver(post_save, sender=Opportunity)
def track_opportunity_changes(sender, instance, created, **kwargs):
    """Registra mudanças em oportunidades"""
    if created:
        change_type = 'CRIADA'
        change_details = {
            'titulo': instance.title,
            'cliente': str(instance.client),
            'status': instance.status,
        }
    else:
        key = f'opportunity_{instance.pk}'
        old_values = _previous_values.get(key, {})
        
        changes = {}
        for field in old_values.keys():
            old_val = old_values.get(field)
            new_val = getattr(instance, field, None)
            if field == 'status':
                new_val = instance.status
            elif field == 'value_brl':
                new_val = str(instance.value_brl) if instance.value_brl else None
            elif field == 'expected_delivery_date':
                new_val = str(instance.expected_delivery_date) if instance.expected_delivery_date else None
            elif field == 'delivery_date':
                new_val = str(instance.delivery_date) if instance.delivery_date else None
            elif field == 'responsible_user':
                new_val = instance.responsible_user_id
            elif field == 'sales_model':
                new_val = instance.sales_model_id
            
            if old_val != new_val:
                changes[field] = {
                    'de': old_val,
                    'para': new_val
                }
        
        if not changes:
            return
        
        change_type = 'ATUALIZADA'
        change_details = changes
    
    OpportunityHistory.objects.create(
        opportunity=instance,
        changed_by=get_current_user(),
        change_type=change_type,
        change_details=json.dumps(change_details, ensure_ascii=False)
    )


@receiver(pre_save, sender=Stage)
def track_stage_pre_save(sender, instance, **kwargs):
    """Armazena valores anteriores antes de salvar"""
    try:
        obj = sender.objects.get(pk=instance.pk)
        _previous_values[f'stage_{instance.pk}'] = {
            'name': obj.name,
            'order': obj.order,
        }
    except sender.DoesNotExist:
        pass


@receiver(post_save, sender=Stage)
def track_stage_changes(sender, instance, created, **kwargs):
    """Registra mudanças em etapas"""
    if created:
        change_type = 'CRIADA'
        change_details = {
            'nome': instance.name,
            'ordem': instance.order,
            'oportunidade': str(instance.opportunity),
        }
    else:
        key = f'stage_{instance.pk}'
        old_values = _previous_values.get(key, {})
        
        changes = {}
        if old_values.get('name') != instance.name:
            changes['nome'] = {
                'de': old_values.get('name'),
                'para': instance.name
            }
        if old_values.get('order') != instance.order:
            changes['ordem'] = {
                'de': old_values.get('order'),
                'para': instance.order
            }
        
        if not changes:
            return
        
        change_type = 'ATUALIZADA'
        change_details = changes
    
    StageHistory.objects.create(
        stage=instance,
        changed_by=get_current_user(),
        change_type=change_type,
        change_details=json.dumps(change_details, ensure_ascii=False)
    )


@receiver(pre_save, sender=Activity)
def track_activity_pre_save(sender, instance, **kwargs):
    """Armazena valores anteriores antes de salvar"""
    try:
        obj = sender.objects.get(pk=instance.pk)
        _previous_values[f'activity_{instance.pk}'] = {
            'title': obj.title,
            'description': obj.description,
            'status': obj.status,
            'assigned_to': obj.assigned_to_id,
            'expected_date': str(obj.expected_date) if obj.expected_date else None,
            'approved': obj.approved,
        }
    except sender.DoesNotExist:
        pass


@receiver(post_save, sender=Activity)
def track_activity_changes(sender, instance, created, **kwargs):
    """Registra mudanças em atividades"""
    if created:
        change_type = 'CRIADA'
        change_details = {
            'titulo': instance.title,
            'status': instance.status,
            'atribuida_para': str(instance.assigned_to) if instance.assigned_to else 'Não atribuída',
        }
    else:
        key = f'activity_{instance.pk}'
        old_values = _previous_values.get(key, {})
        
        changes = {}
        if old_values.get('title') != instance.title:
            changes['titulo'] = {
                'de': old_values.get('title'),
                'para': instance.title
            }
        if old_values.get('status') != instance.status:
            changes['status'] = {
                'de': old_values.get('status'),
                'para': instance.status
            }
        if old_values.get('assigned_to') != instance.assigned_to_id:
            changes['atribuida_para'] = {
                'de': str(old_values.get('assigned_to')),
                'para': str(instance.assigned_to) if instance.assigned_to else 'Não atribuída'
            }
        if old_values.get('approved') != instance.approved:
            changes['aprovada'] = {
                'de': old_values.get('approved'),
                'para': instance.approved
            }
        
        if not changes:
            return
        
        change_type = 'ATUALIZADA'
        change_details = changes
    
    ActivityHistory.objects.create(
        activity=instance,
        changed_by=get_current_user(),
        change_type=change_type,
        change_details=json.dumps(change_details, ensure_ascii=False)
    )
