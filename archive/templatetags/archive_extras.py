from django import template

register = template.Library()


@register.filter
def human_key(value):
    """Replace underscores with spaces and title-case the result."""
    return str(value).replace('_', ' ').title()
