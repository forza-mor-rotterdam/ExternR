import logging

from django import template

register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def taaktype_url(context, taaktype):
    return taaktype.taaktype_url(context.get("request"))
