from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255, unique=1)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    is_favourite = models.BooleanField(default=False)
    slug = models.SlugField(unique=1)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
