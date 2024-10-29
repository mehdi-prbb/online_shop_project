from django.shortcuts import render

from .models import Product


def product_list(request):
    products = Product.objects.prefetch_related('variants__color', 'attribute_values__attribute').all()
    context = {
        'products': products
    }
    return render(request, 'products/list.html', context)


