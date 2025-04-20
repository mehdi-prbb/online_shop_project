from django.forms import ValidationError
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model

from accounts.models import CustomUser

from ..forms import ReplyForm

from ..models import (
                    Category, Color,
                    Product, ProductAttributeValue,
                    Variant, Attribute, Comment
                    )
from . test_mixins import (
                        AttributeModelSetupMixin,
                        CategoryModelSetupMixin,
                        ColorModelSetupMixin,
                        ProductModelSetupMixin,
                        CommentModelSetupMixin,
                        MockSetupMixin
                        )


class ProductListViewTest(
                        ProductModelSetupMixin,
                        CategoryModelSetupMixin,
                        TestCase
                        ):
    
    def test_view_returns_correct_products(self):
        url = reverse('products:product_list', kwargs={'slug': self.new_category.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.context)
        products = response.context['products']
        self.assertEqual(products.count(), 1)
        self.assertIn(self.product, products)

    def test_view_uses_correct_template(self):
        url = reverse('products:product_list', kwargs={'slug': self.new_category.slug})
        response = self.client.get(url)

        self.assertTemplateUsed(response, 'products/list.html')

    def test_view_handles_invalid_category(self):
        url = reverse('products:product_list', kwargs={'slug': 'invalid-category'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class ProductDetailViewTest(
                            CommentModelSetupMixin,
                            TestCase
                            ):
    def test_view_returns_correct_product(self):
        url = reverse('products:product_details', kwargs={'product_slug': self.product.slug})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('product', response.context)
        comments = response.context['comments']
        self.assertEqual(comments.count(), 1)
        self.assertIn(self.comment_2, comments)

        self.assertIn('comment_form', response.context)
        # print(response.context['comment_form'])
        # print(ReplyForm)
        self.assertIsInstance(response.context['comment_form'], ReplyForm)

    def test_view_uses_correct_template(self):
        # Test that the view uses the correct template
        url = reverse('products:product_details', kwargs={'product_slug': self.product.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'products/detail.html')




class CommentCreateViewTest(CommentModelSetupMixin, TestCase):
    def test_comment_creation(self):
        self.client.login(username='mehdi', password='12345')
        
        # Simulate a POST request
        url = reverse('products:comment_create', kwargs={'product_slug': self.product.slug})
        response = self.client.post(url, data={'content': 'This is a test comment.'})
        
        # Check the response and database
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.content, 'This is a test comment.')
        self.assertEqual(comment.product, self.product)
        self.assertEqual(comment.user, self.user_1)

        # Check if the success message was added
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Comment successfully created')