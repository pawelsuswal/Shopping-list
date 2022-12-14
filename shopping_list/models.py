from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from products.models import UNITS_OF_MEASUREMENT, Product
from shops.models import Shop


class ShoppingList(models.Model):
    """Representation of shopping list"""
    name = models.CharField(max_length=255)
    is_finished = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    is_favourite = models.BooleanField(default=False)
    show_bought = models.BooleanField(default=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, blank=True, null=True)
    products = models.ManyToManyField(Product, through='ProductShoppingList')
    shared_with_list = models.ManyToManyField(get_user_model(), related_name='shared_with',  blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class ProductShoppingList(models.Model):
    """Representation of relation between shopping lists and products"""
    shopping_list = models.ForeignKey('ShoppingList', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_bought = models.BooleanField(default=False)
    amount = models.FloatField(validators=[MinValueValidator(0)],
                               blank=True,
                               null=True, )
    unit_of_measurement = models.CharField(max_length=20,
                                           choices=UNITS_OF_MEASUREMENT,
                                           blank=True,
                                           null=True, )
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Shopping list: {self.shopping_list.name}, product: {self.product.name}'
