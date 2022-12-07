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

    # def save(self, commit=True):
    #     shop = super().save(commit=False)
    #     shop.user = self.request.user
    #
    #     shops = Shop.objects.filter(name=shop.name, user=shop.user)
    #     if shops:
    #         shop_db = shops.first()
    #         shop_db.is_active = True
    #         shop_db.is_favourite = shop.is_favourite
    #         for shop_category in shop_db.shopcategory_set.all():
    #             shop_category.is_active = False
    #             shop_category.order = -1
    #         shop = shop_db
    #
    #     if commit:
    #         shop.save()
    #         shop_categories = shop.shopcategory_set.all()
    #
    #         for count, category in enumerate(self.request.POST.getlist('categories')):
    #             shop_category = shop_categories.filter(category=category)
    #             if shop_category:
    #                 shop_category.order = count
    #                 shop_category.is_active = True
    #                 continue
    #             else:
    #                 shop.shopcategory_set.create(category_id=category, order=count)
    #
    #     return shop
