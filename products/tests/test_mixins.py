from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client


from ..models import Attribute, Category, Color, Product, Comment

class CategoryModelSetupMixin:
    """
    Mixin to set up a primary and nested category instance for testing.
    """
    def create_valid_category(self, **kwargs):
        obj = Category(**kwargs)
        obj.full_clean()
        obj.save()
        return obj

    def setUp(self):
        super().setUp()

        self.category = self.create_valid_category(
            title = 'Mobile',
            is_active = True
        )
        self.new_category = self.create_valid_category(
            title="Home Appliances",
            )
        self.child_category = self.create_valid_category(
            title = 'Samsung',
            parent = self.category,
            is_active = True
        )
        self.new_child_category = self.create_valid_category(
            title = 'Xiaomi',
            parent = self.category,
            is_active = True
        )
        self.inactive_category = self.create_valid_category(
            title = 'Inactive Category',
            is_active = False
        )
        self.active_category = self.create_valid_category(
            title = 'Active Category',
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
                slug = 'asus',
                description = 'asus description',
                cover_image = self.mock_image,
                is_active = True
        )

        self.new_product = Product.objects.create(
                category = self.new_category,
                name = 'Lenovo',
                slug = 'lenovo',
                description = 'Lenovo description',
                cover_image = self.mock_image,
                is_active = True
        )


class AttributeModelSetupMixin:
    """
    Mixin to set up a Attribute instance for testing.
    """
    def setUp(self):
        super().setUp()

        self.attribute = Attribute.objects.create(
            name = 'Screen size',
        )

        self.new_attribute = Attribute.objects.create(
            name = 'Os type',
        )



User = get_user_model()
class UserModelSetupMixin:
    def setUp(self):
        super().setUp()

        self.user_1 = User.objects.create_user(
                                            phone='09031234567',
                                            password= None
                                            )
        self.user_2 = User.objects.create_user(
                                            phone='09028990847',
                                            password= None
                                            )
        self.user_3 = User.objects.create_user(
                                            phone='09019925077',
                                            password= None
                                            )


class CommentModelSetupMixin(
                            ProductModelSetupMixin,
                            UserModelSetupMixin
                            ):
    """
    Mixin to set up a Comment instance for testing.
    """
    def setUp(self):
        super().setUp()

        self.comment_1 = Comment.objects.create(
            user = self.user_3,
            product = self.product,
            content = 'asus comment 1',
            status = 'w'
        )

        self.comment_2 = Comment.objects.create(
            user = self.user_1,
            product = self.product,
            parent = self.comment_1,
            content = 'comment 1 reply',
            status = 'p'
        )

        self.comment_3 = Comment.objects.create(
            user = self.user_2,
            product = self.product,
            content = 'second comment',
            status = 'c'
        )