# Generated by Django 5.1.1 on 2025-04-06 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_productimage_remove_product_images_product_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='product',
            name='specifications',
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='subcategory',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
