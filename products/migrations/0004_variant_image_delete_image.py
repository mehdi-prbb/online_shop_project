# Generated by Django 5.1.1 on 2024-10-13 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_image_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='variant',
            name='image',
            field=models.ImageField(default='alternative_image', upload_to='products_images/'),
        ),
        migrations.DeleteModel(
            name='Image',
        ),
    ]
