from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client


from ..models import Attribute, Brand, Category, Color, Product, Comment, CategoryType


class CtaegoryTypeModelSetupMixin:
    def setUp(self):
        super().setUp()

        self.category_type = CategoryType.objects.create(
            title = 'Main',
            slug = 'main',
            verbose_name = 'main category'
        )


class CategoryModelSetupMixin(CtaegoryTypeModelSetupMixin):
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
            category_type = self.category_type,
            is_active = True
        )

        self.category_1 = self.create_valid_category(
            title = 'Best sellers',
            category_type = self.category_type,
            is_active = True
        )

        self.new_category = self.create_valid_category(
            title="Home Appliances",
            category_type = self.category_type,
            )
        self.child_category = self.create_valid_category(
            title = 'Samsung',
            category_type = self.category_type,
            parent = self.category,
            is_active = True
        )
        self.new_child_category = self.create_valid_category(
            title = 'Xiaomi',
            category_type = self.category_type,
            parent = self.category,
            is_active = True
        )
        self.inactive_category = self.create_valid_category(
            title = 'Inactive Category',
            category_type = self.category_type,
            is_active = False
        )
        self.active_category = self.create_valid_category(
            title = 'Active Category',
            category_type = self.category_type,
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


class BrandModelSetupMixin(MockSetupMixin):
    def setUp(self):
        super().setUp()
        self.brand = Brand.objects.create(
            title = 'Samsung',
            slug = 'samsung',
            logo = self.mock_image
        )

        self.brand_2 = Brand.objects.create(
            title = 'Lenovo',
            slug = 'lenovo',
            logo = self.mock_image
        )

        self.brand_3 = Brand.objects.create(
            title = 'Asus',
            slug = 'asus',
            logo = self.mock_image
        )


class ProductModelSetupMixin(CategoryModelSetupMixin, BrandModelSetupMixin, MockSetupMixin):
     """
     Mixin to set up a Product instance and its dependencies for testing.
     """
     def setUp(self):
        super().setUp()
        self.product = Product.objects.create(
                # category = self.category,
                name = 'Asus',
                slug = 'asus',
                brand = self.brand_3,
                description = 'asus description',
                cover_image = self.mock_image,
                is_active = True
        )
        self.product.category.add(self.category, self.category_1)
        self.categories = self.product.category.all()

        self.new_product = Product.objects.create(
                # category = self.new_category,
                name = 'Lenovo',
                slug = 'lenovo',
                brand = self.brand_2,
                description = 'Lenovo description',
                cover_image = self.mock_image,
                is_active = True
        )
        self.new_product.category.add(self.new_category)


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