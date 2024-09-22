from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Safely get a value from a dictionary using a key."""
    if isinstance(d, dict) and key in d:
        return d.get(key)
    return ""