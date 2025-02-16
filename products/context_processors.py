from .models import Category


def category_context_processor(request):
    categories = Category.objects.filter(is_active=True)
    context = {
        "categories": categories
    }
    return context