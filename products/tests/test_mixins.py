from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client


from ..models import Attribute, Category, Color, Product, Comment

class CategoryModelSetupMixin:
    """
    Mixin to set up a primary and nested category instance for testing.
    """
    def setUp(self):
        super().setUp()

        self.category = Category.objects.create(
            title = 'Mobile',
            is_active = True
        )

        self.category.clean()
        self.category.save()

        self.new_category = Category.objects.create(
            title="Home Appliances",
            )
        
        self.new_category.clean()
        self.new_category.save()

        self.child_category = Category.objects.create(
            title = 'Samsung',
            parent = self.category,
            is_active = True
        )

        self.child_category.clean()
        self.child_category.save()

        self.new_child_category = Category.objects.create(
            title = 'Xiaomi',
            parent = self.category,
            is_active = True
        )

        self.new_child_category.clean()
        self.new_child_category.save()

        self.inactive_category = Category.objects.create(
            title = 'Inactive Category',
            is_active = False
        )

        self.inactive_category.clean()
        self.inactive_category.save()

        self.active_category = Category.objects.create(
            title = 'Active Category',
            is_active = True
        )

        self.active_category.clean()
        self.active_category.save()


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
                # category = self.category,
                name = 'Asus',
                slug = 'asus',
                description = 'asus description',
                cover_image = self.mock_image,
                is_active = True
        )

        self.new_product = Product.objects.create(
                # category = self.category,
                name = 'Lenovo',
                slug = 'lenovo',
                description = 'Lenovo description',
                cover_image = self.mock_image,
                is_active = True
        )
        # self.product.category.add([self.category.id])
        # self.product.category.set([self.category])
        self.product.category.set([self.new_category])
        # print(self.product.category.set([self.child_category]))
        # print('+++++++++++++++++++++++++++++++')
        # print(self.child_category.parent)
        # print(self.category)
        # print(self.product.category.all())


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
                                            username='mehdi',
                                            password='12345'
                                            )
        self.user_2 = User.objects.create_user(
                                            username='negar',
                                            password='54321'
                                            )
        self.user_3 = User.objects.create_user(
                                            username='ali',
                                            password='12345'
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