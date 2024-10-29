from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Attribute, Category, Color, Product

class CategoryModelSetupMixin:
    """
    Mixin to set up a primary and nested category instance for testing.
    """
    def setUp(self):
        super().setUp()

        self.category = Category.objects.create(
            title = 'Mobile',
            slug = 'mobile',
            is_active = True
        )

        self.new_category = Category.objects.create(
            title="Home Appliances",
            slug="home-appliances"
            )

        self.child_category = Category.objects.create(
            title = 'Samsung',
            slug = 'samsung',
            parent = self.category,
            is_active = True
        )

        self.new_child_category = Category.objects.create(
            title = 'Xiaomi',
            slug = 'xiaomi',
            parent = self.category,
            is_active = True
        )


class ColorModelSetupMixin:
    """
    Mixin to set up a Color instance for testing.
    """
    def setUp(self):
        super().setUp()

        self.color = Color.objects.create(
            name='Red',
            code='#FF0000'  # Assuming the ColorField accepts hex values
        )

        self.new_color = Color.objects.create(
            name='White',
            code='#FFFFFF'  
        )

class MockSetupMixin:
    """
    Mixin to set up a mock image file for testing image fields.
    """
    def setUp(self):
        super().setUp()
        self.mock_image = SimpleUploadedFile(
            name = 'test_image.jpg',
            content = b'\x47\x49\x46\x38\x39\x61',
            content_type = 'image/jpeg'
        )


class ProductModelSetupMixin(CategoryModelSetupMixin, MockSetupMixin):
     """
     Mixin to set up a Product instance and its dependencies for testing.
     """
     def setUp(self):
        super().setUp()
        self.product = Product.objects.create(
                category = self.category,
                name = 'Asus',
                description = 'asus description',
                cover_image = self.mock_image,
                is_active = True
        )

        self.new_product = Product.objects.create(
                category = self.category,
                name = 'Lenovo',
                description = 'Lenovo description',
                cover_image = self.mock_image,
                is_active = True
        )


class AttributeModelSetupMixin(CategoryModelSetupMixin):
    """
    Mixin to set up a Attribute instance for testing.
    """
    def setUp(self):
        super().setUp()

        self.attribute = Attribute.objects.create(
            name = 'Screen size',
            category = self.category
        )

        self.new_attribute = Attribute.objects.create(
            name = 'Os type',
            category = self.category
        )