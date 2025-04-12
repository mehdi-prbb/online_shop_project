# Generated by Django 5.1.1 on 2025-04-02 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_customuser_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtpCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=11, unique=True)),
                ('code', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
