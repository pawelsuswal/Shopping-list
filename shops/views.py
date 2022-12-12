from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django import views

from shops.forms import CreateShopForm
from shops.models import Shop


class ShopCreateView(LoginRequiredMixin, CreateView):
    success_url = reverse_lazy('shops:list')
    model = Shop
    form_class = CreateShopForm
    template_name = 'shops/create.html'
    context_object_name = 'shop'

    def form_valid(self, form):
        user = self.request.user
        name = form.cleaned_data['name']
        is_favourite = form.cleaned_data['is_favourite']
        categories = form.cleaned_data['categories']
        shop = Shop.objects.create(user=user, name=name, is_favourite=is_favourite)
        for count, category in enumerate(categories):
            shop.shopcategory_set.create(category=category, order=count)

        return redirect('shops:list')

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super(ShopCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class ShopUpdateView(LoginRequiredMixin, UpdateView):
    success_url = reverse_lazy('shops:list')
    model = Shop
    form_class = CreateShopForm
    template_name = 'shops/create.html'
    context_object_name = 'shop'

    def form_valid(self, form):
        shop = form.save(commit=False)
        shop_categories = shop.shopcategory_set.all()

        if 'categories' in form.changed_data:
            categories_id_list = list(form.cleaned_data['categories'].order_by('name').values_list('id', flat=True))
            order_to_assign = -1

            for shop_category in shop_categories:
                if shop_category.category_id not in categories_id_list:
                    shop_category.delete()
                else:
                    categories_id_list.remove(shop_category.category_id)
                    if shop_category.order > order_to_assign:
                        order_to_assign = shop_category.order

            for category_id in categories_id_list:
                order_to_assign += 1
                shop.shopcategory_set.create(category_id=category_id, order=order_to_assign)

            for count, shop_category in enumerate(shop.shopcategory_set.all()):
                shop_category.order = count
                shop_category.save()

        shop.save()
        return redirect('shops:list')

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super(ShopUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class ShopDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('shops:list')
    model = Shop
    template_name = '../templates/delete_confirmation.html'
    extra_context = {'cancel_operation_url': 'shops:list'}


class ShopListView(LoginRequiredMixin, ListView):
    template_name = 'shops/list.html'
    model = Shop
    context_object_name = 'shops'
    allow_empty = 1

    def get_queryset(self):
        return Shop.objects.filter(user=self.request.user).order_by('-is_favourite', 'name')


class ShopCategoriesReorderedView(LoginRequiredMixin, views.View):
    def get(self, request, slug):
        user = request.user
        shop_categories = get_object_or_404(Shop, user=user, slug=slug).shopcategory_set.order_by('order')
        return render(request, 'shops/reorder_categories.html', {'shop_categories': shop_categories})

    @staticmethod
    def _move_top(shop, shop_category):
        shop_category.order = -1
        shop_category.save()
        for count, shop_category in enumerate(shop.shopcategory_set.all().order_by('order')):
            shop_category.order = count
            shop_category.save()

    @staticmethod
    def _move_up(shop, shop_category):
        if shop_category.order > 0:
            shop_category_prev = shop.shopcategory_set.get(order=shop_category.order - 1)
            shop_category_prev.order = shop_category.order
            shop_category.order -= 1

            shop_category_prev.save()
            shop_category.save()

    @staticmethod
    def _move_down(shop, shop_category):
        if shop_category.order < shop.shopcategory_set.all().count() - 1:
            shop_category_next = shop.shopcategory_set.get(order=shop_category.order + 1)
            shop_category_next.order = shop_category.order
            shop_category.order += 1

            shop_category_next.save()
            shop_category.save()

    @staticmethod
    def _move_bottom(shop, shop_category):
        shop_category.order = -1
        shop_category.save()
        for count, shop_category in enumerate(shop.shopcategory_set.all().order_by('order')):
            shop_category.order = count
            shop_category.save()

    def post(self, request, slug, category):
        user = request.user
        shop = get_object_or_404(Shop, user=user, slug=slug)
        shop_category = shop.shopcategory_set.get(category_id=category)

        if 'top' in request.POST:
            self._move_top(shop, shop_category)

        elif 'up' in request.POST:
            self._move_up(shop, shop_category)

        elif 'down' in request.POST:
            self._move_down(shop, shop_category)

        elif 'bottom' in request.POST:
            self._move_bottom(shop, shop_category)

        return redirect('shops:reorder', slug)
