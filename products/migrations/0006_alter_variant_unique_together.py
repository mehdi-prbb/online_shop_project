# Generated by Django 5.1.1 on 2024-10-26 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_alter_product_description'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='variant',
            unique_together={('color', 'product')},
        ),
    ]