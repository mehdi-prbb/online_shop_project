from .models import Category, Product
from django.db.models import Prefetch


def category_context_processor(request):
    categories = Category.objects.filter(is_active=True)

    return {
        'categories': categories,
    }