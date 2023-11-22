from django import template
from django.template.defaultfilters import stringfilter

import markdown as md

register = template.Library()


# Para poder visualizar el contenido de una manera más ordenada
@register.filter()
@stringfilter #que solo permita devolver cadenas de textos
def markdown(value):
    return md.markdown(value, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.toc',
    ])