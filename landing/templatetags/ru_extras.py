
from django import template
 
register = template.Library()
 
 
def _form(n, forms):
    n = abs(int(n))
    if 11 <= n % 100 <= 14:
        return forms[2]
    if n % 10 == 1:
        return forms[0]
    if 2 <= n % 10 <= 4:
        return forms[1]
    return forms[2]
 
 
@register.filter
def ru_word(value, variants):
    """{{ 5|ru_word:"событие,события,событий" }} -> событий"""
    try:
        forms = [v.strip() for v in variants.split(',')]
        return _form(value, forms) if len(forms) >= 3 else ''
    except (ValueError, TypeError):
        return ''
 
 
@register.filter
def ru_plural(value, variants):
    """{{ 5|ru_plural:"событие,события,событий" }} -> 5 событий"""
    word = ru_word(value, variants)
    return f"{value} {word}" if word else value
 
















