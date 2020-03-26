from django import template
register = template.Library()

@register.filter
def my_index(List, i):
    return List[int(i)]