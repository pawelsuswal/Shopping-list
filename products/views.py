import itertools

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from products.forms import CreateProductForm
from products.models import Product


class ProductCreateView(LoginRequiredMixin, CreateView):
    success_url = reverse_lazy('products:list')
    model = Product
    form_class = CreateProductForm
    template_name = 'products/create.html'
    context_object_name = 'product'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super(ProductCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    success_url = reverse_lazy('products:list')
    model = Product
    form_class = CreateProductForm
    template_name = 'products/create.html'

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super(ProductUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('products:list')
    model = Product
    template_name = '../templates/delete_confirmation.html'
    #todo poprawić link w zalezności na której zakładce jest użytkownik
    extra_context = {'cancel_operation_url': 'products:list'}


class ProductListView(LoginRequiredMixin, ListView):
    template_name = 'products/list.html'
    model = Product
    context_object_name = 'products'
    allow_empty = 1

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user).order_by('-is_favourite', 'category__name', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_products = context['products']

        categories_for_favourite_products, categories_for_not_favourite_products = get_categories_by_favourite(
            all_products)
        context['categories_for_favourite_products'] = categories_for_favourite_products
        context['categories_for_not_favourite_products'] = categories_for_not_favourite_products
        return context


def get_categories_by_favourite(all_products):
    categories_for_favourite_products = all_products.filter(is_favourite=True).values_list('category__name')
    categories_for_favourite_products = set(categories_for_favourite_products)
    categories_for_favourite_products = list(itertools.chain(*categories_for_favourite_products))

    categories_for_not_favourite_products = all_products.filter(is_favourite=False).values_list('category__name')
    categories_for_not_favourite_products = set(categories_for_not_favourite_products)
    categories_for_not_favourite_products = list(itertools.chain(*categories_for_not_favourite_products))

    if None in categories_for_favourite_products:
        categories_for_favourite_products[categories_for_favourite_products.index(None)] = ''

    if None in categories_for_not_favourite_products:
        categories_for_not_favourite_products[categories_for_not_favourite_products.index(None)] = ''

    categories_for_favourite_products.sort()
    categories_for_not_favourite_products.sort()
    return categories_for_favourite_products, categories_for_not_favourite_products
