from django import forms
from django.forms import RadioSelect

from categories.models import Category
from products.models import Product


class CreateProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ('name', 'is_favourite', 'default_amount', 'default_uom', 'category')
        widgets = {'category': RadioSelect()}

    def __init__(self, *args, **kwargs):
        """Setup queryset for categories to show only categories related for current user"""
        self.request = kwargs.pop('request')
        super(CreateProductForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=self.request.user)

