# Generated by Django 3.2.16 on 2022-12-23 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_alter_category_name'),
        ('shops', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='categories',
            field=models.ManyToManyField(blank=True, through='shops.ShopCategory', to='categories.Category'),
        ),
    ]
