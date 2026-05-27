from django import template

register = template.Library()

@register.filter
def peso_chileno(value):
    try:
        valor = float(value)
        entero = int(valor)
        return f"${entero:,}".replace(",", ".")
    except (ValueError, TypeError):
        return value