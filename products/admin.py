from django import forms
from django.contrib import admin
from django.db.models import Sum
from django.contrib.admin import ModelAdmin, TabularInline

from . models import (
                    Category, Color,
                    Product, Variant,
                    ProductAttributeValue, Attribute
                    )


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """
    Customizes the admin interface for the Category model.

    Configures which fields are displayed in the list view, enables search, 
    prepopulates the slug field based on the title, and filters by title.
    """
    list_display = ['id', 'title', 'parent', 'is_active', ]
    list_display_links = ['id', 'title']
    search_fields = ['title']
    autocomplete_fields = ['parent']
    readonly_fields = ['slug']
    
    @admin.display(description='parent', ordering='category')
    def parent(self, obj):
        return obj.parent

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent__parent__parent')

class VariantInline(TabularInline):
    """
    Inline admin interface for managing Variant instances 
    associated with a parent model (e.g., Product).
    
    Allows adding, editing, and removing Variants directly 
    within the parent model's admin form.
    """
    model = Variant
    extra = 1
    fields = ['color', 'image', 'price', 'stock']
    autocomplete_fields = ['color']


class ProductAttributeValueInline(TabularInline):
    """
    Inline admin interface for managing ProductAttributeValue instances 
    associated with a parent model (e.g., Product).
    
    Allows for adding, editing, and removing Product Attribute Values 
    directly within the parent model's admin form.
    """
    model = ProductAttributeValue
    extra = 1
    fields = ['attribute', 'value']
    autocomplete_fields = ['attribute']


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    """
    Customizes the admin interface for the Product model.
    
    Configures the display of Product instances, search capabilities, 
    filters, inlines for related models, and custom queryset behavior 
    for optimizing performance.
    """
    list_display = ['id', 'name', 'product_category',
                    'total_stock', 'tag_list', 'created_at',
                    'updated_at','is_active']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'description', 'category__slug']
    list_filter = ['name', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('category',)
    autocomplete_fields = ['category']
    inlines = [ProductAttributeValueInline, VariantInline]

    def get_queryset(self, request):
        """
        Customizes the queryset for the admin list view to optimize performance.
        
        Selects related parent categories and annotates the queryset with 
        the total stock of all variants for each product.
        """
        qs = super().get_queryset(request)
        return qs.annotate(total_stock=Sum('variants__stock')).prefetch_related('category', 'tags')
    
    @admin.display(description='Total Stock', ordering='total_stock')
    def total_stock(self, obj):
        """
        Returns the total stock for a given product.
        
        This value is displayed in the admin list view as 'Total Stock'.
        """
        return obj.total_stock

    @admin.display(description='Categories', ordering='category')
    def product_category(self, obj):
        return " | ".join([cat.slug for cat in obj.category.all()])
    
    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
    
    
@admin.register(Attribute)
class AttributeAdmin(ModelAdmin):
    """
    Customizes the admin interface for the Attribute model.
    
    Configures the display of Attribute instances, search capabilities, 
    filters by category, and optimizes the queryset for performance.
    """
    list_display = ['name',]
    search_fields = ['name']

@admin.register(Color)
class ColorAdmin(ModelAdmin):
    """
    Customizes the admin interface for the Color model.
    
    Configures the display of Color instances and search capabilities 
    for easy lookup by name.
    """
    list_display = ['id', 'name', 'code']
    search_fields = ['name']

