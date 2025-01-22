from django.views.generic import ListView
from django.db.models import Prefetch

from .models import Product, Category



class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'

    def get_queryset(self):
        # Fetch the category by slug (or any other identifier)
        category_slug = self.kwargs.get('slug')  

        category = Category.objects.get(slug=category_slug)

        print(category.get_descendants())

        queryset = Product.objects.filter(category__slug__in=[category])
        return queryset
    
