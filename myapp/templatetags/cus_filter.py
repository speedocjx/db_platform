from django import template
from myapp.include.encrypt import prpcrypt
register = template.Library()

@register.filter
def descrypt(values):
    py = prpcrypt()
    values = py.decrypt(values)
    return values


@register.filter
def s_to_d(values):
    values = int(values/3600/24)
    return str(values)+'d'