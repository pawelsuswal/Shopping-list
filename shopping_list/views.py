from django import views
from django.shortcuts import render, redirect

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

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

    def get_context_data(self, **kwargs):
        context = super(ShoppingListCreateView, self).get_context_data(**kwargs)
        user = self.request.user
        all_products = Product.objects.filter(user=user).order_by('-is_favourite', 'name')
        categories_for_favourite_products, categories_for_not_favourite_products = get_categories_by_favourite(
            all_products)
        products_by_categories_and_favourites = [[True, []]]
        for category in categories_for_favourite_products:
            if category != '':
                products_by_categories_and_favourites[0][1].append([category,
                                                                    all_products.filter(category__name=category,
                                                                                        is_favourite=True).order_by(
                                                                        'name')])
            else:
                products_by_categories_and_favourites[0][1].append([category,
                                                                    all_products.filter(category=None,
                                                                                        is_favourite=True).order_by(
                                                                        'name')])

        products_by_categories_and_favourites.append([False, []])
        for category in categories_for_not_favourite_products:
            if category != '':
                products_by_categories_and_favourites[1][1].append([category,
                                                                    all_products.filter(category__name=category,
                                                                                        is_favourite=False).order_by(
                                                                        'name')])

            else:
                products_by_categories_and_favourites[1][1].append([category,
                                                                    all_products.filter(category=None,
                                                                                        is_favourite=False).order_by(
                                                                        'name')])

        context['products_by_categories_and_favourites'] = products_by_categories_and_favourites
        context['UNITS_OF_MEASUREMENT'] = UNITS_OF_MEASUREMENT
        return context

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        products_to_save = []

        for item in self.request.POST.items():
            if 'product' not in item[0]:
                continue

            product_id = int(item[0].split('-id-')[1])
            product = Product.objects.filter(user=user, id=product_id)

            if not product:
                return super().form_invalid(form)

            product_id = str(product_id)
            amount = self.request.POST[''.join(('amount-id-', product_id))]
            uom = self.request.POST[''.join(('uom-id-', product_id))]
            comment = self.request.POST[''.join(('comment-id-', product_id))]

            if amount == '':
                amount = None
            else:
                try:
                    amount = float(amount)
                except ValueError:
                    return super().form_invalid(form)

            if (not any(uom in uom_code for uom_code in UNITS_OF_MEASUREMENT) and uom != 'None'):
                return super().form_invalid(form)

            if uom == 'None':
                uom = None

            products_to_save.append({
                'product': product,
                'amount': amount,
                'uom': uom,
                'comment': comment,
            })

        # shopping_list.save()
        shopping_list = form.save()

        for product_to_save in products_to_save:
            shopping_list.productshoppinglist_set.create(
                product=product_to_save['product'].first(),
                amount=product_to_save['amount'],
                unit_of_measurement=product_to_save['uom'],
                comment=product_to_save['comment'],
            )

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

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super(ShoppingListUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class ShoppingListDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('shopping_list:list')
    model = ShoppingList
    template_name = '../templates/delete_confirmation.html'
    extra_context = {'cancel_operation_url': 'shopping_list:list'}


class ShoppingListListView(LoginRequiredMixin, views.View):
    def get(self, request):
        user = request.user

        data_to_render = []
        shopping_lists = ShoppingList.objects.filter(user=user)

        for shopping_list in shopping_lists:
            shop_categories = list(
                shopping_list.shop.categories.all().order_by('shopcategory__order').values_list('name'))
            shop_categories = [item[0] for item in shop_categories]
            products = ProductShoppingList.objects.raw(
                '''select * from shopping_list_productshoppinglist as psl 
                left join products_product as p on p.id = psl.product_id
                left join shops_shopcategory as sc on (p.category_id = sc.category_id and sc.shop_id = %s )
                where shopping_list_id = %s
                ''',
                [shopping_list.shop_id, shopping_list.id])
            # print('*' * 20)
            # print(shop_categories)
            # print(products)
            # print(type(products2))
            products = [item for item in products]
            uom = dict(UNITS_OF_MEASUREMENT)
            for product in products:
                if product.order is None:
                    product.order = -1
                if product.amount is None:
                    product.amount = ''
                if product.unit_of_measurement is not None:
                    product.unit_of_measurement = uom[product.unit_of_measurement]

            products = sorted(products, key=lambda x: (x.order, x.product.name,))
            #
            # print(p1)
            # for p in p1:
            #     print(p.order)
            # for k in p:
            #     print(k)
            # print(sorted(products, key=lambda x: shop_categories.index(x.category.name)))
            # print('*' * 20)

            data_to_render.append([shopping_list, products])
        return render(request, 'shopping_list/list.html', {'data_to_render': data_to_render})


class ShoppingListUpdateProductStatus(LoginRequiredMixin, views.View):
    def get(self, request, slug, product_id):
        shopping_list = ShoppingList.objects.filter(slug=slug)

        if shopping_list:
            shopping_list = shopping_list.first()
            p = shopping_list.productshoppinglist_set.get(product_id=product_id)
            p.is_bought = not p.is_bought
            p.save()

        return redirect('shopping_list:list')


class ShoppingListViewComment(LoginRequiredMixin, views.View):

    def get(self, request, slug, product_id):
        shopping_list = ShoppingList.objects.filter(slug=slug)
        if not shopping_list:
            return redirect('shopping_list:list')

        product = shopping_list.first().productshoppinglist_set.filter(product_id=product_id)
        if not product:
            return redirect('shopping_list:list')

        return render(request, 'shopping_list/view_comment.html', {'product': product.first()})

    # def get_queryset(self):
    #
    #     queryset = super().get_queryset()
    #     shopping_list = queryset.filter(shopping_list__slug=self.kwargs['slug'],
    #                                     product=self.kwargs['product_id']).first().shopping_list
    #     # .filter(shopping_list_id=shopping_list.id, product=self.kwargs['product_id'])
    #     return queryset

    # return ShoppingList.objects.filter(slug=self.kwargs['slug'], products=self.kwargs['product_id'])
