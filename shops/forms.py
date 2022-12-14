from django import forms

from categories.models import Category
from .models import Shop


class CreateShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ('name', 'is_favourite', 'categories')
        widgets = {
            'categories': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        """Setup queryset to select categories only related to current user"""
        self.request = kwargs.pop('request')
        super(CreateShopForm, self).__init__(*args, **kwargs)
        self.fields['categories'].queryset = Category.objects.filter(
            user=self.request.user)
