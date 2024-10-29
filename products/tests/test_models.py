from django.test import TestCase
from django.db.utils import IntegrityError

from ..models import (
                    Category, Color,
                    Product, ProductAttributeValue,
                    Variant, Attribute
                    )
from . test_mixins import (
                        AttributeModelSetupMixin,
                        CategoryModelSetupMixin,
                        ColorModelSetupMixin,
                        ProductModelSetupMixin,
                        MockSetupMixin
                        )


class CategoryModelTest(
                        CategoryModelSetupMixin,
                        TestCase
                        ):
    """
    Tests for the Category model.
    """
    def test_category_creation(self):
        """Test Category model creation."""
        self.assertEqual(self.category.title, 'Mobile')
        self.assertEqual(self.category.slug, 'mobile')
        self.assertTrue(self.category.is_active)
        # Check that category has no parent.
        self.assertIsNone(self.category.parent)

    def test_cascade_delete(self):
        """Test that deleting the parent category
        deletes associated child categories."""
        self.category.delete()
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=self.child_category.id)
    
    def test_parent_child_relationship(self):
        """Test the self-referencing ForeignKey for subcategories."""
        self.assertEqual(self.child_category.parent, self.category)
        self.assertIn(self.child_category, self.category.subcategories.all())

    def test_update_foreign_key(self):
        """Test updating the subcategories category foreign key."""
        self.category.child_category = self.new_child_category
        self.category.save()
        self.assertEqual(self.category.child_category, self.new_child_category)

    def test_category_str_method(self):
        """Test the __str__ method of the category model."""
        self.assertEqual(str(self.category), 'Mobile')


class ProductModelTest(
                    ProductModelSetupMixin,
                    TestCase
                    ):
    """
    Tests for the Product model.
    """
    def test_product_creation(self):
        """Test product creation."""
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.name, 'Asus')
        self.assertEqual(self.product.description, 'asus description')
        self.assertTrue(
                        self.product.cover_image.name.\
                        startswith('products_cover_image/test_image')
                        )
        self.assertTrue(self.product.cover_image.name.endswith('.jpg'))
        self.assertTrue(self.product.is_active)

    def test_product_without_category(self):
        """Test that creating a product without
        a category raises an IntegrityError."""
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name="Smartphone",
                description="A smartphone without a category"
            )

    def test_product_creation_with_default_cover_image(self):
        """Test that a Product instance has the
        default cover_image when not specified."""
        product = Product.objects.create(
            category=self.category,
            name='Smartphone',
            description='A high-end smartphone',
        )
        
        self.assertEqual(product.cover_image, 'alternative_image')

    def test_cascade_delete(self):
        """Test that deleting the category
        deletes associated products."""
        self.category.delete()
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(id=self.product.id)

    def test_product_category_relationship(self):
        """Test that the category's reverse
        relationship includes the product."""
        self.assertEqual(self.product.category, self.category)
        self.assertIn(self.product, self.category.products.all())

    def test_update_foreign_key(self):
        """Test updating the product's category foreign key."""
        self.product.category = self.new_category
        self.product.save()
        self.assertEqual(self.product.category, self.new_category)

    def test_product_str_method(self):
        """Test the __str__ method of the Product model."""
        self.assertEqual(str(self.product), 'Asus')


class ColorModelTest(ColorModelSetupMixin, TestCase):
    """
    Tests for the Color model.
    """
    def test_color_creation(self):
        """Test that a Color instance can be created successfully."""
        self.assertEqual(self.color.name, 'Red')
        self.assertEqual(self.color.code, '#FF0000')

    def test_color_str(self):
        """Test the __str__ method of the Color model."""
        self.assertEqual(str(self.color), 'Red #FF0000')


class VariantModelTest(
                    ProductModelSetupMixin,
                    ColorModelSetupMixin,
                    MockSetupMixin,
                    TestCase
                    ):
    """
    Tests for the Variant model.
    """

    def setUp(self):
        """
        Set up test data for the Variant model tests. 
        Creates a Variant instance linked to a predefined product and color.
        """
        super().setUp()

        self.variant = Variant.objects.create(
            product = self.product,
            color = self.color,
            image = self.mock_image,
            price = 140.00,
            stock = 1
        )
    
    def test_variant_creation(self):
        """Test product creation."""
        self.assertEqual(self.variant.product, self.product)
        self.assertEqual(self.variant.color, self.color)
        self.assertTrue(
                        self.variant.image.name.\
                        startswith('products_images/test_image')
                        )
        self.assertTrue(self.variant.image.name.endswith('.jpg'))
        self.assertEqual(self.variant.price, 140.00)
        self.assertEqual(self.variant.stock, 1)

    def test_variant_without_product(self):
        """Test that creating a variant without a
        product raises an IntegrityError."""
        with self.assertRaises(IntegrityError):
            Variant.objects.create(
                color = self.color,
                price=140.00,
                stock=1
            )

    def test_variant_without_color(self):
        """Test that creating a variant without a
        color raises an IntegrityError."""
        with self.assertRaises(IntegrityError):
            Variant.objects.create(
                product = self.product,
                price=140.00,
                stock=1
            )
        
    def test_variant_creation_with_default_image(self):
        """Test that a Variant instance has the
        default image when not specified."""
        
        # Another product and color was created to avoid the
        # error of uniqueness of product and color combination
        self.category = Category.objects.create(
                                        title='Electronics',
                                        slug='electronics'
                                        )
        self.product = Product.objects.create(
            category=self.category,
            name='Smartphone',
            description='High-end smartphone'
        )

        self.color = Color.objects.create(name='Green', code='#00ff00')

        variant = Variant.objects.create(
            product=self.product,
            color=self.color,
            price=10.00,
            stock=1,
        )
        self.assertEqual(variant.image, 'alternative_image')

    def test_product_cascade_delete(self):
        """Test that deleting the category deletes associated products."""
        self.product.delete()
        with self.assertRaises(Variant.DoesNotExist):
            Variant.objects.get(id=self.variant.id)

    def test_color_cascade_delete(self):
        """Test that deleting the category deletes associated products."""
        self.color.delete()
        with self.assertRaises(Variant.DoesNotExist):
            Variant.objects.get(id=self.variant.id)

    def test_variant_product_relationship(self):
        """Test that the product's reverse
        relationship includes the variant."""
        self.assertEqual(self.variant.product, self.product)
        self.assertIn(self.variant, self.product.variants.all())

    def test_variant_color_relationship(self):
        """Test that the product's reverse
        relationship includes the variant."""
        self.assertEqual(self.variant.color, self.color)
        self.assertIn(self.variant, self.color.color_variants.all())

    def test_update_color_foreign_key(self):
        """Test updating the variant's color foreign key."""
        self.variant.color = self.new_color
        self.variant.save()
        self.assertEqual(self.variant.color, self.new_color)
        
    def test_update_product_foreign_key(self):
        """Test updating the variant's product foreign key."""
        self.variant.product = self.new_product
        self.variant.save()
        self.assertEqual(self.variant.product, self.new_product)

    def test_variant_unique_together(self):
        """
        Test that the unique_together constraint on
        the Variant model prevents duplicate product-color
        combinations by raising an IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            Variant.objects.create(
                product=self.product,
                color=self.color,
                price=799.99,
                stock=5
            )

    def test_variant_str(self):
        """Test the __str__ method of the variant model."""
        self.assertEqual(str(self.variant), '')


class AttributeModelTest(
                        AttributeModelSetupMixin,
                        CategoryModelSetupMixin,
                        TestCase
                        ):
    """
    Tests for the Attribute model.
    """

    def test_attribute_creation(self):
        """Test Attribute creation."""
        self.assertEqual(self.attribute.name, 'Screen size')
        self.assertEqual(self.attribute.category, self.category)

    def test_attribute_without_category(self):
        """Test that creating a attribute without a
        category raises an IntegrityError."""
        with self.assertRaises(IntegrityError):
            Attribute.objects.create(
                name = self.attribute.name,
            )

    def test_category_cascade_delete(self):
        """Test that deleting the category deletes associated attributes."""
        self.category.delete()
        with self.assertRaises(Attribute.DoesNotExist):
            Attribute.objects.get(id=self.attribute.id)

    def test_attribute_category_relationship(self):
        """Test that the category's reverse
        relationship includes the attributes."""
        self.assertEqual(self.attribute.category, self.category)
        self.assertIn(self.attribute, self.category.attributes.all())

    def test_update_category_foreign_key(self):
        """Test updating the attribute's category foreign key."""
        self.attribute.category = self.new_category
        self.attribute.save()
        self.assertEqual(self.attribute.category, self.new_category)

    def test_attribute_unique_together(self):
        """
        Test that the unique_together constraint on the
        Attribute model prevents duplicate name-category
        combinations by raising an IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            Attribute.objects.create(
                name=self.attribute.name,
                category=self.category
            )

    def test_attribute_str(self):
        """Test the __str__ method of the Attribute model."""
        self.assertEqual(
                    f"{self.attribute.name} {self.category}",
                    "Screen size Mobile"
                    )


class ProductAttributeValueModelTest(
                                    AttributeModelSetupMixin,
                                    ProductModelSetupMixin,
                                    TestCase
                                    ):
    """
    Tests for the ProductAttributeValue model.
    """

    def setUp(self):
        """
        Set up test data for the ProductAttributeValue model tests. 
        Creates a ProductAttributeValue instance linked to a predefined 
        product and attribute with a specific value.
        """
        super().setUp()

        self.attribute_value = ProductAttributeValue.objects.create(
            product = self.product,
            attribute = self.attribute,
            value = '6.2'
        )

    def test_attribute_value_creation(self):
        self.assertEqual(self.attribute_value.product, self.product)
        self.assertEqual(self.attribute_value.attribute, self.attribute)
        self.assertEqual(self.attribute_value.value, '6.2')

    def test_attribute_value_without_product(self):
        """Test that creating a attribute_value without
        a product raises an IntegrityError."""
        with self.assertRaises(IntegrityError):
            ProductAttributeValue.objects.create(
                attribute = self.attribute,
                value = '6.2'
            )

    def test_attribute_value_without_attribute(self):
        """Test that creating a attribute_value without
        a attribute raises an IntegrityError."""
        with self.assertRaises(IntegrityError):
            ProductAttributeValue.objects.create(
                product = self.product,
                value = '6.2'
            )

    def test_product_cascade_delete(self):
        """Test that deleting the product
        deletes associated attribute_value."""
        self.product.delete()
        with self.assertRaises(ProductAttributeValue.DoesNotExist):
            ProductAttributeValue.objects.get(id=self.attribute_value.id)

    def test_attribute_cascade_delete(self):
        """Test that deleting the attribute
        deletes associated attribute_value."""
        self.attribute.delete()
        with self.assertRaises(ProductAttributeValue.DoesNotExist):
            ProductAttributeValue.objects.get(id=self.attribute_value.id)

    def test_attribute_value_product_relationship(self):
        """Test that the product's reverse
        relationship includes the attribute_value."""
        self.assertEqual(self.attribute_value.product, self.product)
        self.assertIn(self.attribute_value, self.product.attribute_values.all())

    def test_attribute_value_attribute_relationship(self):
        """Test that the attributes's reverse
        relationship includes the attribute_value."""
        self.assertEqual(self.attribute_value.attribute, self.attribute)
        self.assertIn(self.attribute_value, self.attribute.values.all())

    def test_update_product_foreign_key(self):
        """Test updating the attribute_values's product foreign key."""
        self.attribute_value.product = self.new_product
        self.attribute_value.save()
        self.assertEqual(self.attribute_value.product, self.new_product)

    def test_update_attribute_foreign_key(self):
        """Test updating the attribute_values's attribute foreign key."""
        self.attribute_value.attribute = self.new_attribute
        self.attribute_value.save()
        self.assertEqual(self.attribute_value.attribute, self.new_attribute)

    def test_attribute_value_unique_together(self):
        """
        Test that the unique_together constraint on the
        ProductAttributeValue model prevents duplicate
        product-attribute combinations by raising an IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            ProductAttributeValue.objects.create(
                product = self.product,
                attribute = self.attribute,
                value = '6.2'
            )

    def test_attribute_value_str(self):
        """Test the __str__ method of the ProductAttributeValue model."""
        self.assertEqual(str(self.attribute_value), "")