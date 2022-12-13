import itertools

from django import views
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from friends.models import UserFriend
from products.models import Product, UNITS_OF_MEASUREMENT
from products.views import get_categories_by_favourite
from shopping_list.forms import CreateShoppingListForm, ShowCommentForm
from shopping_list.models import ShoppingList, ProductShoppingList


class ShoppingListCreateView(LoginRequiredMixin, CreateView):
    success_url = reverse_lazy('shopping_list:list')
    model = ShoppingList
    form_class = CreateShoppingListForm
    template_name = 'shopping_list/create.html'
    context_object_name = 'shopping_list'

    def get_initial(self):
        user = self.request.user
        source_slug = self.request.GET.get('source')
        source_shopping_list = ShoppingList.objects.filter(user=user, slug=source_slug)
        initial = super().get_initial()

        if source_shopping_list.exists():
            initial['name'] = source_shopping_list.first().name
            initial['shop'] = source_shopping_list.first().shop

        return initial

    def get_context_data(self, **kwargs):
        context = super(ShoppingListCreateView, self).get_context_data(**kwargs)
        user = self.request.user
        source_slug = self.request.GET.get('source')
        source_shopping_list = ShoppingList.objects.filter(user=user, slug=source_slug)

        if source_shopping_list:
            source_shopping_list = source_shopping_list.first()
        else:
            source_shopping_list = None

        context['products_by_categories_and_favourites'] = get_all_products(user, source_shopping_list)
        context['UNITS_OF_MEASUREMENT'] = UNITS_OF_MEASUREMENT
        context['source_shopping_list'] = source_shopping_list
        return context

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        try:
            products_to_save = get_products_for_shopping_list(user, self.request.POST)
            shopping_list = form.save()
            user_id = str(shopping_list.user_id)
            shopping_list_id = str(shopping_list.id)
            shopping_list.slug = slugify('-'.join((user_id, shopping_list_id)))
            shopping_list.save()
            save_products_in_shopping_list(products_to_save, shopping_list)
        except ValueError:
            return super().form_invalid(form)
        except ObjectDoesNotExist:
            return super().form_invalid(form)

        return redirect('shopping_list:list')

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super(ShoppingListCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class ShoppingListUpdateView(LoginRequiredMixin, UpdateView):
    success_url = reverse_lazy('shopping_list:list')
    model = ShoppingList
    form_class = CreateShoppingListForm
    template_name = 'shopping_list/create.html'

    def get_context_data(self, **kwargs):
        context = super(ShoppingListUpdateView, self).get_context_data(**kwargs)
        user = self.request.user

        shopping_list = context['shoppinglist']

        context['products_by_categories_and_favourites'] = get_all_products(user, shopping_list)
        context['UNITS_OF_MEASUREMENT'] = UNITS_OF_MEASUREMENT
        return context

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super(ShoppingListUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        try:
            products_to_save = get_products_for_shopping_list(user, self.request.POST)
            shopping_list = form.save()
            clear_products_in_shopping_list(shopping_list)
            save_products_in_shopping_list(products_to_save, shopping_list)
        except ValueError:
            return super().form_invalid(form)
        except ObjectDoesNotExist:
            return super().form_invalid(form)

        return redirect('shopping_list:list')


class ShoppingListDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('shopping_list:list')
    model = ShoppingList
    template_name = '../templates/delete_confirmation.html'
    extra_context = {'cancel_operation_url': 'shopping_list:list'}


class ShoppingListListView(LoginRequiredMixin, views.View):
    def get(self, request):
        user = request.user

        shopping_lists = ShoppingList.objects.filter(Q(user=user) | Q(shared_with_list=user),
                                                     is_finished=False).order_by('-created_on')
        data_to_render = get_shopping_lists(shopping_lists, user)

        return render(request, 'shopping_list/main_list.html', {'data_to_render': data_to_render})


class ShoppingListUpdateProductStatus(LoginRequiredMixin, views.View):
    def get(self, request, slug, product_id):
        user = request.user
        shopping_list = ShoppingList.objects.filter(user=user, slug=slug)

        if shopping_list:
            shopping_list = shopping_list.first()
            p = shopping_list.productshoppinglist_set.get(product_id=product_id)
            p.is_bought = not p.is_bought
            p.save()

        return redirect('shopping_list:list')


class ShoppingListViewComment(LoginRequiredMixin, views.View):

    def get(self, request, slug, product_id):
        user = request.user
        previous = request.GET.get('previous')

        shopping_list = ShoppingList.objects.filter(user=user, slug=slug)
        if not shopping_list:
            return redirect('shopping_list:list')

        product = shopping_list.first().productshoppinglist_set.filter(product_id=product_id)
        if not product:
            return redirect('shopping_list:list')

        return render(request, 'shopping_list/view_comment.html', {'product': product.first(), 'previous': previous})

    def post(self, request, slug, product_id):
        previous = request.POST.get('previous')
        return redirect(previous)


class ShoppingListUpdateFinishStatus(LoginRequiredMixin, views.View):
    # todo czy to jest poprawnie, że baza jest modyfikowana get'em? Przenieść na POST
    def get(self, request, slug):
        user = request.user
        shopping_list = ShoppingList.objects.filter(user=user, slug=slug)

        if shopping_list:
            shopping_list = shopping_list.first()
            shopping_list.is_finished = not shopping_list.is_finished
            shopping_list.save()

        return redirect('shopping_list:list')


class ShoppingListHistoryListView(LoginRequiredMixin, views.View):

    def get(self, request):
        user = request.user

        shopping_lists = ShoppingList.objects.filter(user=user, is_finished=True).order_by('-created_on')
        data_to_render = get_shopping_lists(shopping_lists)

        return render(request, 'shopping_list/history_list.html', {'data_to_render': data_to_render})


class ShoppingListFavouritesListView(LoginRequiredMixin, views.View):

    def get(self, request):
        user = request.user

        shopping_lists = ShoppingList.objects.filter(user=user, is_favourite=True).order_by('created_on')
        data_to_render = get_shopping_lists(shopping_lists)

        return render(request, 'shopping_list/favourites_list.html', {'data_to_render': data_to_render})


class ShoppingListShareView(LoginRequiredMixin, UpdateView):
    model = ShoppingList
    fields = ('name',)
    success_url = reverse_lazy('shopping_list:list')
    template_name = 'shopping_list/friend_list.html'
    context_object_name = 'shopping_list'

    def post(self, request, *args, **kwargs):

        user = request.user
        list_id = request.POST.get('list-id')

        shopping_list = get_object_or_404(ShoppingList, user=user, id=list_id)

        new_share_list = []

        for item in request.POST:
            if 'friend' in item:
                friend_id = item.split('-id-')[1]
                friend = get_object_or_404(UserFriend, user=user, friend_id=friend_id).friend
                new_share_list.append(friend)

        shopping_list.shared_with_list.set(new_share_list)

        return redirect('shopping_list:list')

    # todo czy tutaj zamiast get nie powinno być get_object_or_404? co się stanie jak nie będzie obiektu? można użyć get_object_or_404
    def get_context_data(self, **kwargs):
        context = super(ShoppingListShareView, self).get_context_data()
        user = self.request.user
        shopping_list = context['shopping_list']

        already_shared_with = shopping_list.shared_with_list.all().values_list('id', flat=True)

        friends_list = UserFriend.objects.filter(user=user).order_by('friend__username')
        data_to_display = []

        for friend in friends_list.all():

            if already_shared_with and friend.friend_id in already_shared_with:
                already_shared = True
            else:
                already_shared = False

            data_to_display.append(
                {
                    'friend': friend,
                    'already_shared': already_shared,
                }
            )
        context['data_to_display'] = data_to_display
        return context


def get_all_products(user, shopping_list=None):
    all_products = Product.objects.filter(user=user).order_by('-is_favourite', 'name')
    categories_for_favourite_products, categories_for_not_favourite_products = get_categories_by_favourite(
        all_products)

    products_by_categories_and_favourites = [[True, []], [False, []]]

    for data_set in products_by_categories_and_favourites:
        is_favourite = data_set[0]

        if is_favourite:
            category_set = categories_for_favourite_products
        else:
            category_set = categories_for_not_favourite_products

        for category in category_set:
            if category == '':
                category = None

            products_for_category = all_products.filter(category__name=category, is_favourite=is_favourite).order_by(
                'name')

            products_to_save = []

            for product in products_for_category:
                if shopping_list and product in shopping_list.products.all():
                    product_from_shopping_list = shopping_list.productshoppinglist_set.get(product=product)
                    product_to_save = {
                        'id': product.id,
                        'checked': True,
                        'name': product.name,
                        'amount': product_from_shopping_list.amount,
                        'uom': product_from_shopping_list.unit_of_measurement,
                        'comment': product_from_shopping_list.comment,
                    }

                else:
                    product_to_save = {
                        'id': product.id,
                        'checked': False,
                        'name': product.name,
                        'amount': product.default_amount,
                        'uom': product.default_uom,
                        'comment': '',
                    }

                products_to_save.append(product_to_save)

            if products_to_save:
                data_set[1].append([category, products_to_save])

    return products_by_categories_and_favourites


def get_products_for_shopping_list(user, post_data):
    products_to_save = []

    for item in post_data.items():
        if 'product' not in item[0]:
            continue

        product_id = int(item[0].split('-id-')[1])
        product = Product.objects.filter(user=user, id=product_id)

        if not product:
            raise ObjectDoesNotExist

        product = product.first()
        product_id = str(product_id)
        amount = post_data[''.join(('amount-id-', product_id))]
        uom = post_data[''.join(('uom-id-', product_id))]
        comment = post_data[''.join(('comment-id-', product_id))]

        if amount == '':
            amount = None
        else:
            amount = float(amount)

        if not any(uom in uom_code for uom_code in UNITS_OF_MEASUREMENT) and uom != 'None':
            raise ValueError

        if uom == 'None' or uom == '':
            uom = None

        products_to_save.append({
            'product': product,
            'amount': amount,
            'uom': uom,
            'comment': comment,
        })
    return products_to_save


def save_products_in_shopping_list(products_to_save, shopping_list):
    for product_to_save in products_to_save:
        shopping_list.productshoppinglist_set.update_or_create(
            product=product_to_save['product'],
            defaults={
                'amount': product_to_save['amount'],
                'unit_of_measurement': product_to_save['uom'],
                'comment': product_to_save['comment'],
            }
        )


def clear_products_in_shopping_list(shopping_list: ShoppingList):
    for product in shopping_list.productshoppinglist_set.all():
        product.delete()


def get_shopping_lists(shopping_lists, user=None):
    uom = dict(UNITS_OF_MEASUREMENT)
    data_to_render = []
    for shopping_list in shopping_lists:
        products = []
        if shopping_list.shop is None:
            products_query_set = shopping_list.productshoppinglist_set.all().order_by('product__name')
            for product in products_query_set.all():
                if product.amount is None:
                    product.amount = ''
                if product.unit_of_measurement is not None:
                    product.unit_of_measurement = uom[product.unit_of_measurement]
                products.append(product)

        else:
            products = ProductShoppingList.objects.raw(
                '''select * from shopping_list_productshoppinglist as psl 
                left join products_product as p on p.id = psl.product_id
                left join shops_shopcategory as sc on (p.category_id = sc.category_id and sc.shop_id = %s )
                where shopping_list_id = %s
                ''',
                [shopping_list.shop_id, shopping_list.id])
            products = [item for item in products]

            for product in products:
                if product.order is None:
                    product.order = -1
                if product.amount is None:
                    product.amount = ''
                if product.unit_of_measurement is not None:
                    product.unit_of_measurement = uom[product.unit_of_measurement]

            products = sorted(products, key=lambda x: (x.order, x.product.name,))

        shared = False
        if user is not None and shopping_list.user != user:
            shared = True

        data_to_render.append([shopping_list, products, shared])
    return data_to_render
