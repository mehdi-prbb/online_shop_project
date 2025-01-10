from django.db import connection
from django import forms
from django.contrib import admin
from django.db.models import Prefetch
from django.db.models import Sum
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
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
    list_display = ['id', 'title', 'parent', 'is_active',]
    list_display_links = ['id', 'title']
    readonly_fields = ['slug']
    search_fields = ['title']
    list_filter = ['title']
    autocomplete_fields = ['parent']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch('parent', queryset=Category.objects.all())
        )



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


class ProductAttributeValueForm(forms.ModelForm):
    """
    A form for creating and updating ProductAttributeValue instances.
    
    This form automatically populates the attribute field's queryset 
    with all available attributes, optimizing the query to include 
    their related category.
    """
    class Meta:
        model = ProductAttributeValue
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and modifies the queryset for the attribute field.
        
        This ensures that only attributes associated with categories 
        are available for selection, improving usability.
        """
        super().__init__(*args, **kwargs)
        # Set the queryset for the attribute field to include related categories
        self.fields['attribute'].queryset =\
        Attribute.objects.all().select_related('category')

class ProductAttributeValueInline(TabularInline):
    """
    Inline admin interface for managing ProductAttributeValue instances 
    associated with a parent model (e.g., Product).
    
    Allows for adding, editing, and removing Product Attribute Values 
    directly within the parent model's admin form.
    """
    model = ProductAttributeValue
    form = ProductAttributeValueForm
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
                    'total_stock', 'created_at',
                    'updated_at','is_active']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'description', 'category__slug']
    list_filter = ['name', 'updated_at']
    autocomplete_fields = ['category']
    inlines = [ProductAttributeValueInline, VariantInline]

    def get_queryset(self, request):
        """
        Customizes the queryset for the admin list view to optimize performance.
        
        Selects related parent categories and annotates the queryset with 
        the total stock of all variants for each product.
        """
        qs = super().get_queryset(request)
        return qs.annotate(total_stock=Sum('variants__stock')).select_related('category')

    @admin.display(description='Total Stock', ordering='total_stock')
    def total_stock(self, obj):
        """
        Returns the total stock for a given product.
        
        This value is displayed in the admin list view as 'Total Stock'.
        """
        return obj.total_stock

    @admin.display(description='category', ordering='category')
    def product_category(self, obj):
        return obj.category.slug
    
    
@admin.register(Attribute)
class AttributeAdmin(ModelAdmin):
    """
    Customizes the admin interface for the Attribute model.
    
    Configures the display of Attribute instances, search capabilities, 
    filters by category, and optimizes the queryset for performance.
    """
    list_display = ['name', 'category']
    search_fields = ['name']
    list_filter = ['category']

    def get_queryset(self, request):
        """
        Customizes the queryset for the admin list view to optimize performance.
        
        Uses select_related to reduce the number of queries made when 
        accessing related category data.
        """
        return super().get_queryset(request).select_related('category')


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Customizes the queryset for the foreign key field in the admin form.
        
        Filters the category field to show only active parent categories.
        This improves usability by preventing selection of inactive or 
        non-parent categories.
        """
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.\
                filter(parent__isnull=True, is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Color)
class ColorAdmin(ModelAdmin):
    """
    Customizes the admin interface for the Color model.
    
    Configures the display of Color instances and search capabilities 
    for easy lookup by name.
    """
    list_display = ['id', 'name', 'code']
    search_fields = ['name']

