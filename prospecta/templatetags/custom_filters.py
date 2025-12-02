from django import template
from decimal import Decimal

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
