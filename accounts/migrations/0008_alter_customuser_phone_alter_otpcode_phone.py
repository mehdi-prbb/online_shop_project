# Generated by Django 5.1.1 on 2025-04-09 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_rename_phone_number_customuser_phone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(max_length=11),
        ),
        migrations.AlterField(
            model_name='otpcode',
            name='phone',
            field=models.CharField(max_length=11),
        ),
    ]
