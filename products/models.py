from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from colorfield.fields import ColorField

from .custom_managers import PublishedCommentsManger


class CategoryType(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)
    verbose_name = models.CharField(max_length=250)

    def __str__(self):
        return self.title
    

class Category(models.Model):
    """
    Model representing a product category.
    """
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)
    category_type = models.ForeignKey(
                                    CategoryType,
                                    on_delete=models.SET_NULL,
                                    null=True, blank=True
                                    )
    parent = models.ForeignKey(
                                'self', null=True, blank=True,
                                related_name='sub_cats',
                                on_delete=models.CASCADE
                                )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "categories"
        unique_together = ('title', 'category_type', 'parent')
    
    def category_full_path(self):
        """
        Return full path category.
        """
        full_path = [self.title.lower()]
        parent_name = self.parent
        while parent_name is not None:
            full_path.append(parent_name.title.lower())
            parent_name = parent_name.parent
        return full_path[::-1]
    
    def clean(self):
        category_path = self.category_full_path()
        self.slug = slugify(category_path)

        if Category.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            raise ValidationError(f'A category with slug "{self.slug}" is already exists.')  
         
        if len(category_path) != len(set(category_path)):
            raise ValidationError(f"Category '{self.title}' can't be its own subcategory due to a conflict with '{self.parent}'.")
        
        if len(category_path) > 3:
            raise ValidationError(f"You can't make category '{self.title}' as 4th subcategory, Use tags to make subcategories.'")

        return super().clean()

    def __str__(self):
        full_path = self.category_full_path()
        return ' -> '.join(full_path)


class Brand(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to='brands_logo/')

    def __str__(self):
        return self.title
    

class Product(models.Model):
    """
    Model representing a product in the online shop.
    """
    category = models.ManyToManyField(Category, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    cover_image = models.ImageField(
                                    upload_to='products_cover_image/',
                                    default='alternative_image'
                                    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse("products:product_details",
                       kwargs={"product_slug": self.slug})

    def __str__(self):
        return self.name
    

class Color(models.Model):
    """
     Model representing a color that can be associated with product variants.
    """
    name = models.CharField(max_length=250)
    code = ColorField()

    def __str__(self):
        return f"{self.name} {self.code}"


class Variant(models.Model):
    """
    Model representing a specific variant of a product, such as a color option.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='variants')
    color = models.ForeignKey(
                            Color, on_delete=models.CASCADE,
                            related_name='color_variants'
                            )
    image = models.ImageField(
                            upload_to='products_images/',
                            default='alternative_image'
                            )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    class Meta:
        unique_together = ('color', 'product')

    def __str__(self):
        return ""
    

class Attribute(models.Model):
    """
    Model representing an attribute that can be associated
    with products, like "Size" or "Material".
    """
    name = models.CharField(unique=True, max_length=250)

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """
    Model representing a specific value for a product's
    attribute, such as "Large" for a "Size" attribute.
    """
    product = models.ForeignKey(
                                Product,
                                on_delete=models.CASCADE,
                                related_name='attribute_values'
                                )
    attribute = models.ForeignKey(
                                Attribute, 
                                on_delete=models.CASCADE,
                                related_name='values'
                                )
    value = models.CharField(max_length=50)

    class Meta:
        unique_together = ('product', 'attribute')

    def __str__(self):
        return ""


class Comment(models.Model):
    PUBLISHED = 'p'
    WAITING = 'w'
    CANCELED = 'c'

    PUBLISH_STATUS = [
        (PUBLISHED, 'published'),
        (WAITING, 'waiting'),
        (CANCELED, 'canceled')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='commenters')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    content = models.TextField()
    status = models.CharField(max_length=1, choices=PUBLISH_STATUS, default=WAITING)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    published_comments_manager = PublishedCommentsManger()

    class Meta:
        ordering = ['-created_at']  # Show latest comments first

    def __str__(self):
        return f"Comment by {self.user.username} on {self.product.name}"

    def is_reply(self):
        """
        Check if the comment is a reply to another comment.
        """
        return self.parent is not None
    
    def get_absolute_url(self):
        return reverse("products:product_details", kwargs={"product_slug": self.product.slug})
