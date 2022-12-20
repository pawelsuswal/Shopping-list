from django.contrib import admin

from shopping_list import models

# Register your models here.
admin.site.register(models.ShoppingList)
admin.site.register(models.ProductShoppingList)