from django import template

register = template.Library()

@register.filter
def clp(valor):
    """
    Formatea un número como pesos chilenos con puntos como separadores de miles.
    Ejemplo: 1200000 -> $1.200.000
    """
    try:
        valor = int(valor)
        return "{:,.0f}".format(valor).replace(",", ".")
    except (ValueError, TypeError):
        return valor
