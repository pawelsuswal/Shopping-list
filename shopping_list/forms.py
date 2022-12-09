from django import forms
from django.forms import RadioSelect, CheckboxSelectMultiple, inlineformset_factory, modelformset_factory, \
    BaseModelFormSet, CheckboxInput, BooleanField

from categories.models import Category
from products.models import Product
from shopping_list.models import ShoppingList, ProductShoppingList
from shops.models import Shop


class CreateShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ('name', 'is_favourite', 'shop')
        widgets = {'products': CheckboxSelectMultiple()}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(CreateShoppingListForm, self).__init__(*args, **kwargs)
        self.fields['shop'].queryset = Shop.objects.filter(user=self.request.user)


class ProductsMetaForm(forms.ModelForm):
    class Meta:
        model = ProductShoppingList
        fields = ('product', 'amount', 'unit_of_measurement', 'comment')
        # widgets = {'product': CheckboxSelectMultiple()}

    # def __init__(self, *args, **kwargs):
    # self.request = kwargs.pop('request')
    # super(ProductsMetaForm, self).__init__(*args, **kwargs)
    # self.fields['shop'].queryset = Shop.objects.filter(user=self.request.user)
    # self.fields['product'].queryset = Product.objects.filter(user=self.request.user)


CreateShoppingForm = inlineformset_factory(ShoppingList,
                                           ShoppingList.products.through,
                                           form=ProductsMetaForm)


class TestForm(forms.ModelForm):
    amount = forms.IntegerField()

    class Meta:
        model = Product
        fields = ('name',)
        # widgets = {'name': CheckboxInput()}

    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request')
    #     super(TestForm, self).__init__(*args, **kwargs)
    #     self.fields['name'].queryset = Product.objects.filter(user=self.request.user)
