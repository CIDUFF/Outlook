from django import template
from decimal import Decimal
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def dict_lookup(dictionary, key):
    """
    Permite acesso a dicionários em templates usando sintaxe de filtro.
    Uso: {{ dict|dict_lookup:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def count_true_values(dictionary):
    """
    Conta quantos valores em um dicionário são True.
    Uso: {{ dict|count_true_values }}
    """
    if isinstance(dictionary, dict):
        return sum(1 for v in dictionary.values() if v is True)
    return 0


@register.filter
def multiply(value, arg):
    """
    Multiplica o valor por um argumento.
    Uso: {{ 5|multiply:2 }} resulta em 10
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """
    Divide o valor por um argumento.
    Uso: {{ 10|divide:2 }} resulta em 5
    """
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def format_currency(value):
    """
    Formata valor como moeda brasileira (R$).
    Uso: {{ amount|format_currency }}
    Resultado: R$ 1.234,56
    """
    if value is None or value == '':
        return 'R$ 0,00'

    try:
        # Converter para float
        amount = float(value)

        # Formatar com 2 casas decimais e separador de milhar
        # Usando locale brasileiro
        formatted = f'{amount:,.2f}'.replace(
            ',', '|').replace('.', ',').replace('|', '.')
        return f'R$ {formatted}'
    except (ValueError, TypeError):
        return 'R$ 0,00'


@register.filter
def sum_values(queryset):
    """
    Soma os valores de um queryset de OpportunityCustomValue.
    Uso: {{ opportunity.custom_values.all|sum_values }}
    """
    try:
        total = Decimal('0')
        for item in queryset:
            if hasattr(item, 'value') and item.value:
                total += Decimal(str(item.value))
        return total
    except (ValueError, TypeError):
        return Decimal('0')


@register.filter
def add_decimal(value1, value2):
    """
    Soma dois valores decimais.
    Uso: {{ value1|add_decimal:value2 }}
    """
    try:
        v1 = Decimal(str(value1)) if value1 else Decimal('0')
        v2 = Decimal(str(value2)) if value2 else Decimal('0')
        return v1 + v2
    except (ValueError, TypeError):
        return Decimal('0')


@register.simple_tag
def opportunity_status_badge(opportunity, opportunity_statuses=None):
    """
    Renderiza o badge de status de uma oportunidade.
    Primeiro tenta usar os status customizados (OpportunityStatus),
    caso não encontre, usa os status padrão (hardcoded).
    
    Uso: {% opportunity_status_badge opportunity opportunity_statuses %}
    """
    status_value = opportunity.status
    
    # Tentar buscar status customizado
    if opportunity_statuses:
        for status_obj in opportunity_statuses:
            if status_obj.slug == status_value:
                icon_html = f'<i class="fas {status_obj.icon} mr-1"></i>' if status_obj.icon else ''
                return mark_safe(
                    f'<span class="px-3 py-1 bg-{status_obj.color}-100 text-{status_obj.color}-800 '
                    f'rounded-full text-sm font-semibold">{icon_html}{status_obj.name}</span>'
                )
    
    # Fallback para status padrão (hardcoded)
    status_mapping = {
        'aberta': ('blue', 'Aberta', 'fa-folder-open'),
        'em_andamento': ('yellow', 'Em Andamento', 'fa-spinner'),
        'ganha': ('green', 'Ganha', 'fa-trophy'),
        'perdida': ('red', 'Perdida', 'fa-times-circle'),
        'cancelada': ('gray', 'Cancelada', 'fa-ban'),
    }
    
    color, label, icon = status_mapping.get(status_value, ('gray', status_value, ''))
    icon_html = f'<i class="fas {icon} mr-1"></i>' if icon else ''
    
    return mark_safe(
        f'<span class="px-3 py-1 bg-{color}-100 text-{color}-800 '
        f'rounded-full text-sm font-semibold">{icon_html}{label}</span>'
    )


@register.simple_tag
def get_status_display(status_value, opportunity_statuses=None):
    """
    Retorna apenas o nome do status para exibição.
    
    Uso: {% get_status_display opportunity.status opportunity_statuses %}
    """
    # Tentar buscar status customizado
    if opportunity_statuses:
        for status_obj in opportunity_statuses:
            if status_obj.slug == status_value:
                return status_obj.name
    
    # Fallback para status padrão
    status_mapping = {
        'aberta': 'Aberta',
        'em_andamento': 'Em Andamento',
        'ganha': 'Ganha',
        'perdida': 'Perdida',
        'cancelada': 'Cancelada',
    }
    
    return status_mapping.get(status_value, status_value)
