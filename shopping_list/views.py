from django.forms import modelformset_factory, CheckboxSelectMultiple
from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from products.models import Product, UNITS_OF_MEASUREMENT
from shopping_list.forms import CreateShoppingListForm, CreateShoppingForm, TestForm
from shopping_list.models import ShoppingList


class ShoppingListCreateView(LoginRequiredMixin, CreateView):
    success_url = reverse_lazy('shopping_list:list')
    model = ShoppingList
    form_class = CreateShoppingListForm
    template_name = 'shopping_list/create.html'
    context_object_name = 'shopping_list'

    def get_context_data(self, **kwargs):
        context = super(ShoppingListCreateView, self).get_context_data(**kwargs)
        user = self.request.user
        products = Product.objects.filter(user=user)
        # a =TestForm(request=self.request)
        # print('*' * 20)
        # print(a)
        # print('*' * 20)
        # products1 = modelformset_factory(Product, form=TestForm, extra=0)
        # context['TestForm'] = products1(queryset=Product.objects.filter(user=user))
        context['products'] = products
        context['UNITS_OF_MEASUREMENT'] = UNITS_OF_MEASUREMENT
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

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


class ShoppingListListView(LoginRequiredMixin, ListView):
    template_name = 'shopping_list/list.html'
    model = ShoppingList
    context_object_name = 'shopping_lists'
    allow_empty = 1

    def get_queryset(self):
        return ShoppingList.objects.filter(user=self.request.user, is_finished=False).order_by('created_on')
