from django import template

# Registrar el módulo de filtros
register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    """
    Filtro de plantilla para agregar clases CSS a los widgets de formularios.

    :param value: El campo del formulario al que se le agregará la clase.
    :param css_class: La clase CSS a agregar al widget.
    :return: El widget del formulario con la clase CSS agregada.
    """
    return value.as_widget(attrs={"class": css_class})
