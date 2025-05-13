from django.urls import path

from . import views


app_name = 'products'


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search/category/<slug:cat_slug>/', views.ProductListView.as_view(), name='product_list'),
    path('search/category/<slug:cat_slug>/brand-<slug:brand_slug>/', views.ProductListView.as_view(), name='product_list_by_brand'),
    path('<slug:product_slug>', views.ProductDetailView.as_view(), name='product_details'),
    path('comment/<slug:product_slug>', views.CommentCreateView.as_view(), name='comment_create'),
]

