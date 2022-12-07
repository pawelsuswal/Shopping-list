from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
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

    # todo wyjaśnić obsługę danych i jak skorzystać z is_valid
    #     dodatkowo dowiedzieć sie czy można to zrobić jakoś w form_valid
    def post(self, request, *args, **kwargs):
        name = request.POST['name']
        user = request.user
        if request.POST.get('is_favourite') is None:
            is_favourite = False
        else:
            is_favourite = True

        shop = Shop.objects.create(name=name, user=user, is_favourite=is_favourite)

        for count, category in enumerate(request.POST.getlist('categories')):
            shop.shopcategory_set.create(category_id=category, order=count)

        shop.save()
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

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        user = request.user
        new_categories = request.POST.getlist('categories')
        if request.POST.get('is_favourite') is None:
            is_favourite = False
        else:
            is_favourite = True

        shops = Shop.objects.filter(name=name, user=user)

        if not shops:
            return super(ShopUpdateView, self).post(request)

        shop = shops.first()
        shop.is_favourite = is_favourite
        for shop_category in shop.shopcategory_set.all():
            if shop_category.category_id not in new_categories:
                shop_category.delete()
        for count, shop_category in shop.shopcategory_set.all():
            shop_category.order = count
            shop_category.save()

        categories_count = shop.shopcategory_set.all().count()
        for category in new_categories:
            if category not in shop.shopcategory_set.all().values_list('category_id'):
                shop.shopcategory_set.create(category_id=category, order=categories_count)
                categories_count += 1

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
        shop_categories = Shop.objects.get(slug=slug).shopcategory_set.all().order_by('order')
        return render(request, 'shops/reorder_categories.html', {'shop_categories': shop_categories})

    def post(self, request, slug, category):
        shop = Shop.objects.get(slug=slug)
        shop_category = shop.shopcategory_set.get(category_id=category)

        if 'top' in request.POST:
            shop_category.order = -1
            shop_category.save()

        elif 'up' in request.POST:
            if shop_category.order > 0:
                shop_category_prev = shop.shopcategory_set.get(order=shop_category.order - 1)
                shop_category_prev.order = shop_category.order
                shop_category.order -= 1

                shop_category_prev.save()
                shop_category.save()

        elif 'down' in request.POST:
            if shop_category.order < shop.shopcategory_set.all().count() - 1:
                shop_category_next = shop.shopcategory_set.get(order=shop_category.order + 1)
                shop_category_next.order = shop_category.order
                shop_category.order += 1

                shop_category_next.save()
                shop_category.save()

        elif 'bottom' in request.POST:
            shop_category.order = shop.shopcategory_set.all().count()
            shop_category.save()

        if 'top' in request.POST or 'bottom' in request.POST:
            for count, shop_category in enumerate(shop.shopcategory_set.all().order_by('order')):
                shop_category.order = count
                shop_category.save()

        return redirect('shops:reorder', slug)
