# Generated by Django 5.1.1 on 2024-12-15 19:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_alter_category_slug'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='category',
            unique_together={('title', 'depth')},
        ),
    ]