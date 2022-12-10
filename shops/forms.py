from django import forms

from categories.models import Category
from .models import Shop


class CreateShopForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(CreateShopForm, self).__init__(*args, **kwargs)
        self.fields['categories'].queryset = Category.objects.filter(
            user=self.request.user)


    class Meta:
        model = Shop
        fields = ('name', 'is_favourite', 'categories')
