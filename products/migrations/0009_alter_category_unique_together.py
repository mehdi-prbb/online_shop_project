# Generated by Django 5.1.1 on 2024-12-15 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_alter_category_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='category',
            unique_together={('slug', 'depth')},
        ),
    ]
