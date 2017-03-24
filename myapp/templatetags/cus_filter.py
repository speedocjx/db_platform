from django import template
from myapp.include.encrypt import prpcrypt
register = template.Library()

@register.filter
def descrypt(values):
    py = prpcrypt()
    values = py.decrypt(values)
    return values
