from django import template

register = template.Library()

@register.filter
def color_index(model_number):
    # Use hash for stable index; mod by total color count (e.g. 10)
    return abs(hash(str(model_number))) % 4