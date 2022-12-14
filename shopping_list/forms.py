from django import forms
from django.forms import inlineformset_factory

from shopping_list.models import ShoppingList, ProductShoppingList
from shops.models import Shop


class CreateShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ('name', 'is_favourite', 'shop')

    def __init__(self, *args, **kwargs):
        """Add request data to form and setup queryset to get only current user related objects"""
        self.request = kwargs.pop('request')
        super(CreateShoppingListForm, self).__init__(*args, **kwargs)
        self.fields['shop'].queryset = Shop.objects.filter(user=self.request.user)


class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        """Add request data to form and setup queryset to get only current user related objects"""
        self.request = kwargs.pop('request')
        super(ShoppingListForm, self).__init__(*args, **kwargs)
        self.fields['shop'].queryset = Shop.objects.filter(user=self.request.user)


class ProductsMetaForm(forms.ModelForm):
    class Meta:
        model = ProductShoppingList
        fields = ('product', 'amount', 'unit_of_measurement', 'comment')


class ShowCommentForm(forms.ModelForm):

    class Meta:
        model = ProductShoppingList
        fields = ('comment',)
