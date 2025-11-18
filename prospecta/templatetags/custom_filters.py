from django import template

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
