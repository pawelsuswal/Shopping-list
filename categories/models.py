from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Model of products category"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    is_favourite = models.BooleanField(default=False)
    slug = models.SlugField(unique=1)

    class Meta:
        unique_together = ('name', 'user')

    def save(self, *args, **kwargs):
        """Build custom slug on object save"""
        pk = str(self.user_id)
        name = self.name
        self.slug = slugify('-'.join((pk, name)))
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
