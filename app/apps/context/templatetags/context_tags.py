import logging

from django import template
from django.template.loader import get_template

register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def context_template(context, template_name):
    gebruiker = context.get("request").user
    context_instance = (
        gebruiker.profiel.context
        if gebruiker
        and hasattr(gebruiker, "profiel")
        and hasattr(gebruiker.profiel, "context")
        else None
    )
    default_template = f"standaard/{template_name}"
    if not context_instance:
        return default_template
    try:
        get_template(f"{context_instance.template}/{template_name}")
    except Exception as e:
        logger.error(
            f"Specific template not found, template_name={template_name}, use default: error={e}"
        )
        return default_template

    return f"{context_instance.template}/{template_name}"
