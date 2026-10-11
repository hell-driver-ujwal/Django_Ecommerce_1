from django import template
from store.models import Category

register = template.Library()

@register.inclusion_tag('components/block.html')
def show_product(request):
    pass
