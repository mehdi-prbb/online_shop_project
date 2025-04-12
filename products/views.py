from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.contrib import messages

from .models import Product, Category, Comment
from .forms import ReplyForm



class HomeView(TemplateView):
    template_name = 'products/home.html'


class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')

        category = get_object_or_404(Category, slug=category_slug, is_active=True)

        queryset = Product.objects.filter(category=category)

        return queryset
    

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('variants__color', 'attribute_values__attribute')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = ReplyForm()
        context['comments'] = Comment.published_comments_manager.filter(product=self.object).select_related('user')
        return context


class CommentCreateView(CreateView):
    model = Comment
    form_class = ReplyForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        product_slug = self.kwargs['product_slug']
        product = get_object_or_404(Product, slug=product_slug)
        obj.product = product
        messages.success(self.request, ('Comment successfully created'))
        return super().form_valid(form)
    