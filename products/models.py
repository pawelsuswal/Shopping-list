from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from categories.models import Category

UNITS_OF_MEASUREMENT = [
    ('PCS', 'szt.'),
    ('PCK', 'opak.'),
    ('BTL', 'butelki'),
    ('KG', 'kg'),
    ('DG', 'dag'),
    ('G', 'g')
]


class Product(models.Model):
    """Representation of product"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    is_favourite = models.BooleanField(default=False)
    default_amount = models.FloatField(validators=[MinValueValidator(0)],
                                       blank=True,
                                       null=True)
    default_uom = models.CharField(max_length=20,
                                   choices=UNITS_OF_MEASUREMENT,
                                   blank=True,
                                   null=True)
    slug = models.SlugField(unique=1)

    class Meta:
        unique_together = ('name', 'user')

    def save(self, *args, **kwargs):
        """Build custom slug on object save"""

        pk = str(self.user_id)
        name = self.name
        self.slug = slugify('-'.join((pk, name)))
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
