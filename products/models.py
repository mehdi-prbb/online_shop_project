from django.utils.functional import cached_property
from django.db import models
from django.db.models import Prefetch
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from colorfield.fields import ColorField


class Category(models.Model):
    """
    Model representing a product category.
    """
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey(
                                "self", on_delete=models.CASCADE,
                                related_name='sub_cats',
                                null=True,
                                blank=True
                                )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'categories'

    def clean(self):
        super().clean()
        full_path = self.categoty_path()
        self.slug = slugify(full_path[::-1])
        if Category.objects.filter(slug=self.slug).exists():
            raise ValidationError(f"This category with '{self.slug}' slug already exists.")

    def categoty_path(self):
        path = [self.title]
        parent_name = self.parent
        while parent_name is not None:
            path.append(parent_name.title)
            parent_name = parent_name.parent
        return path
        

    def __str__(self):
        """
        Return full path category.
        """
        full_path = self.categoty_path()
        return ' => '.join(full_path[::-1])
    

class Product(models.Model):
    """
    Model representing a product in the online shop.
    """
    category = models.ForeignKey(
                                Category, on_delete=models.CASCADE,
                                related_name='products'
                                )
    name = models.CharField(max_length=250)
    description = models.TextField()
    cover_image = models.ImageField(
                                    upload_to='products_cover_image/',
                                    default='alternative_image'
                                    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

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
    stock = models.IntegerField()

    class Meta:
        unique_together = ('color', 'product')

    def __str__(self):
        return ""
    

class Attribute(models.Model):
    """
    Model representing an attribute that can be associated
    with products, like "Size" or "Material".
    """
    name = models.CharField(max_length=250)
    category = models.ForeignKey(
                                Category,
                                on_delete=models.CASCADE,
                                related_name='attributes'
                                )
    
    class Meta:
        unique_together = ('name', 'category')

    def __str__(self):
        return f"{self.name} ({self.category})"


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

    
    
    
