from django.db import models

from colorfield.fields import ColorField


class Category(models.Model):
    """
    Model representing a product category.
    """
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
                                "self", on_delete=models.CASCADE,
                                null=True, blank=True,
                                related_name='subcategories'
                                )
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
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

    
    
    
