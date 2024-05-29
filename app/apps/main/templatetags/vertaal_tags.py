from django import template
from utils.constanten import VERTALINGEN

register = template.Library()


@register.filter
def vertaal(value):
    return VERTALINGEN.get(value, value)
