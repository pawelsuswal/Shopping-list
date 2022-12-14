from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from categories.models import Category


# Create your models here.
class Shop(models.Model):
    """Representation of shop"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    is_favourite = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, through='ShopCategory')
    slug = models.SlugField(unique=1)

    class Meta:
        unique_together = ('name', 'user')

    def save(self, *args, **kwargs):
        """Build custom slug on object save"""
        pk = str(self.user_id)
        name = self.name
        self.slug = slugify('-'.join((pk, name)))
        super(Shop, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ShopCategory(models.Model):
    """Representation of relation between shops and categories"""
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    order = models.IntegerField()

    class Meta:
        unique_together = ('shop', 'category')

    def __str__(self):
        return f'Shop: {self.shop}, category: {self.category}, order: {self.order}'
