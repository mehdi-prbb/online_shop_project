# Generated by Django 5.1.1 on 2024-10-26 20:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_alter_variant_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='variant',
            unique_together=set(),
        ),
    ]