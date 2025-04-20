from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import (
                    Category, Color,
                    Product, ProductAttributeValue,
                    Variant, Comment
                    )
from . test_mixins import (
                        AttributeModelSetupMixin,
                        CategoryModelSetupMixin,
                        ColorModelSetupMixin,
                        ProductModelSetupMixin,
                        MockSetupMixin,
                        CommentModelSetupMixin,
                        UserModelSetupMixin
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
        self.assertIn(self.child_category, self.category.sub_cats.all())

    def test_update_foreign_key(self):
        """Test updating the subcategories category foreign key."""
        self.category.child_category = self.new_child_category
        self.category.save()
        self.assertEqual(self.category.child_category, self.new_child_category)

    def test_category_slug_generation(self):
        self.assertEqual(self.category.slug, 'mobile')
        self.assertEqual(self.child_category.slug, 'mobile-samsung')

    def test_category_slug_unique(self):
        """Test that two categories with the same slug raise a ValidationError."""
        duplicate_category = Category(title=self.category.title)
        # Validate the second category (this should raise a ValidationError due to the duplicate slug)
        with self.assertRaises(ValidationError):
            duplicate_category.clean()


    def test_category_full_path(self):
        self.assertEqual(
                        self.child_category.category_full_path(),
                        [self.category.title.lower(),
                        self.child_category.title.lower()]
                         )

    def test_inactive_category_not_shown_in_active(self):
        """Test that inactive categories are excluded from active categories."""
        # Assuming you have a queryset to fetch active categories
        active_categories = Category.objects.filter(is_active=True)
        self.assertIn(self.active_category, active_categories)
        self.assertNotIn(self.inactive_category, active_categories)

    def test_category_with_parent(self):
        """Test assigning a parent category."""
        parent = self.category

        self.assertEqual(self.child_category.parent, parent)

    def test_category_str_method(self):
        """Test the __str__ method of the category model."""
        self.assertEqual(str(self.category), 'mobile')



class ProductModelTest(
                    ProductModelSetupMixin,
                    TestCase
                    ):
    """
    Tests for the Product model.
    """

    def test_create_product(self):
    # Test product creation
        self.assertEqual(self.product.name, "Asus")
        self.assertEqual(self.product.slug, "asus")
        self.assertEqual(self.product.description, "asus description")
        self.assertTrue(self.product.is_active)  # Default value should be True
        self.assertIsNotNone(self.product.created_at)  # Created at should be set
        self.assertIsNotNone(self.product.updated_at)  # Updated at should be set
        # Test the category relationship
        self.assertEqual(self.product.category, self.category)
    
    def test_cascade_delete(self):
        """Test that deleting the category
        deletes associated products."""
        self.category.delete()
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(id=self.product.id)

    def test_product_creation_with_default_cover_image(self):
        """Test that a Product instance has the
        default cover_image when not specified."""
        product = Product.objects.create(
            name='Smartphone',
            category=self.category,
            description='A high-end smartphone',
        )
        
        self.assertEqual(product.cover_image, 'alternative_image')

    def test_update_category(self):
        """Test updating the product's category many to many."""
        self.product.category = self.new_category
        self.product.save()
        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.category, self.new_category)

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

        self.color2 = Color.objects.create(name='Green', code='#00ff00')

        variant = Variant.objects.create(
            product=self.product,
            color=self.color2,
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
                        TestCase
                        ):
    """
    Tests for the Attribute model.
    """

    def test_attribute_creation(self):
        """Test Attribute creation."""
        self.assertEqual(self.attribute.name, 'Screen size')

    def test_attribute_str(self):
        """Test the __str__ method of the Attribute model."""
        self.assertEqual(
                    f"{self.attribute.name}",
                    "Screen size"
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


class CommentModelTest(
                    CommentModelSetupMixin,
                    TestCase
                    ):
    def test_create_comment(self):
        self.assertEqual(self.comment_1.user, self.user_3)
        self.assertEqual(self.comment_1.product, self.product)
        self.assertIsNone(self.comment_1.parent)
        self.assertEqual(self.comment_1.status, 'w')
        self.assertFalse(self.comment_1.is_reply())

    def test_create_reply_comment(self):
        self.assertEqual(self.comment_2.user, self.user_1)
        self.assertEqual(self.comment_2.product, self.product)
        self.assertEqual(self.comment_2.parent, self.comment_1)
        self.assertEqual(self.comment_2.status, 'p')
        self.assertTrue(self.comment_2.is_reply())

    def test_get_absolute_url(self):
        expected_url = reverse("products:product_details", kwargs={"product_slug": self.product.slug})
        self.assertEqual(self.comment_1.get_absolute_url(), expected_url)

    def test_user_cascade_delete(self):
        """Test that deleting the comment author
        deletes associated comment."""
        User = get_user_model()
        self.user_3.delete()
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=self.comment_1.id)

    def test_product_cascade_delete(self):
        """Test that deleting the product
        deletes associated comment."""
        self.product.delete()
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=self.comment_1.id)

    def test_parent_cascade_delete(self):
        """Test that deleting the comment
        deletes associated reply."""
        self.comment_1.delete()
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=self.comment_2.id)

    def test_published_comments_manager(self):

        published_comments = Comment.published_comments_manager.all()

        # comment_1 and comment_3 status are not published.
        self.assertEqual(published_comments.count(), 1)
        self.assertEqual(published_comments.first(), self.comment_2)
        self.assertNotIn(self.comment_1, published_comments)
        self.assertNotIn(self.comment_3, published_comments)

