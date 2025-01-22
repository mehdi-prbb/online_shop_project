from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from colorfield.fields import ColorField
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    """
    Model representing a product category.
    """
    title = models.CharField(max_length=250)
    slug = models.SlugField(blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='sub_cats', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "categories"

    def clean(self):

        if self.parent:
            self.slug = slugify(f"{self.parent} {self.title}")
        else:
            self.slug = slugify(self.title)

        if Category.objects.filter(slug=self.slug).exists():
            raise ValidationError(f'A category with slug "{self.slug}" is already exists.')

        return super().clean()
        
    
    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.title}"
        return self.title
    

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

    
    
    
