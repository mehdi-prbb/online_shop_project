# Generated by Django 5.1.1 on 2025-02-19 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_customuser_managers_customuser_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
