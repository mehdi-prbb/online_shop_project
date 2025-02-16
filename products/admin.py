from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import admin, messages
from django.db.models import Sum
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib.admin import ModelAdmin, TabularInline

from . models import (
                    Category, Color,
                    Product, Variant,
                    ProductAttributeValue, Attribute,
                    Comment
                    )

from .forms import ReplyForm


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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at', 'status', 'reply_button')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'product__name', 'content')
    actions = ['publish_comments', 'cancel_comments']
    list_editable = ['status']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=True).prefetch_related('replies')  # Show all comments, both top-level and replies

    def reply_button(self, obj):
        # Show "Show Replies" button if the comment has replies
        if obj.replies.exists():
            return format_html('<a class="button" href="{}">Show Reply</a>', self.get_reply_url(obj))
        # Otherwise, show "Reply" button for the comment
        else:
            return format_html('<a class="button" href="{}">Reply</a>', self.get_reply_url(obj))

    def get_reply_url(self, obj):
        # URL to reply or show replies to the comment
        if obj.replies.exists():
            return f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.pk}/show_replies/"
        return f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.pk}/reply/"

    def publish_comments(self, request, queryset):
        update_status = queryset.update(status='p')
        self.message_user(request, f'{update_status} comment(s) changed to published.', messages.SUCCESS)
    
    def cancel_comments(self, request, queryset):
        update_status = queryset.update(status='c')
        self.message_user(request, f'{update_status} comment(s) changed to canceled.', messages.SUCCESS)

    def get_urls(self):
        """
        Add custom URL patterns for handling show replies and reply actions.
        """
        urls = super().get_urls()
        custom_urls = [
            path('<int:comment_id>/show_replies/', self.show_replies_view, name='show_replies'),
            path('<int:comment_id>/reply/', self.reply_view, name='reply'),
            path('reply/<int:reply_id>/update/', self.update_reply, name='update_reply'),
            path('reply/<int:reply_id>/delete/', self.delete_reply, name='delete_reply'),
        ]
        return custom_urls + urls

    def show_replies_view(self, request, comment_id):
        comment = Comment.objects.get(pk=comment_id)
        replies = comment.replies.all()  # Get all replies for the comment
        
        context = {
            'comment': comment,
            'replies': replies,
        }
        return TemplateResponse(request, "admin/show_replies.html", context)

    def reply_view(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        if request.method == "POST":
            form = ReplyForm(request.POST)
            if form.is_valid():
                # Create a new comment as a reply
                reply = form.save(commit=False)
                reply.parent = comment
                reply.user = request.user  # or any admin user
                reply.product = comment.product  # Set the product to the parent comment's product
                reply.status = Comment.PUBLISHED  # Set the status to waiting, or another logic
                reply.save()

                comment.status = Comment.PUBLISHED
                comment.save()
                # Redirect to the comment change page after saving the reply
                self.message_user(request, "Reply successfully added.", messages.SUCCESS)
                return redirect(f"/admin/products/comment/")
        else:
            form = ReplyForm()

        context = {
            'comment': comment,
            'form': form,
        }

        return render(request, "admin/reply_comment.html", context)
    
    def update_reply(self, request, reply_id):
        reply = get_object_or_404(Comment, pk=reply_id)
        if request.method == "POST":
            form = ReplyForm(request.POST, instance=reply)
            if form.is_valid():
                form.save()
                self.message_user(request, "Reply updated successfully.", messages.SUCCESS)
                return redirect(f"/admin/products/comment/")
        else:
            form = ReplyForm(instance=reply)

        context = {
            'reply': reply,
            'form': form,
        }

        return render(request, "admin/reply_update.html", context)

    def delete_reply(self, request, reply_id):
        reply = get_object_or_404(Comment, pk=reply_id)
        parent_comment = reply.parent
        reply.delete()
        self.message_user(request, "Reply deleted successfully.", messages.SUCCESS)
        return redirect(f"/admin/products/comment/")