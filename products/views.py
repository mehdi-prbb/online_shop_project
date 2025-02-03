from django.views.generic import ListView
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from .models import Product, Category



class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')

        category = get_object_or_404(Category, slug=category_slug, is_active=True)

        queryset = Product.objects.filter(category=category)

        return queryset
    


