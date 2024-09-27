from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Safely get a value from a dictionary using a key."""
    if isinstance(d, dict) and key in d:
        return d.get(key)
    return ""

@register.filter(name='capitalize_first')
def capitalize_first(value):
    """Capitalize the first letter of the string."""
    return value.capitalize()