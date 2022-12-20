from django import views
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import CreateView, UpdateView, DeleteView

from friends.models import UserFriend
from products.models import UNITS_OF_MEASUREMENT
from shopping_list.forms import CreateShoppingListForm
from shopping_list.mixins import ShoppingListMixins
from shopping_list.models import ShoppingList


class ShoppingListCreateView(LoginRequiredMixin, CreateView, ShoppingListMixins):
    """Display view for create new category"""
    success_url = reverse_lazy('shopping_list:list')
    model = ShoppingList
    form_class = CreateShoppingListForm
    template_name = 'shopping_list/create.html'
    context_object_name = 'shopping_list'

    def get_initial(self):
        """Setup initial values for new shopping list in case building it from template shopping list"""

        user = self.request.user
        source_slug = self.request.GET.get('source')
        source_shopping_list = ShoppingList.objects.filter(user=user, slug=source_slug)
        initial = super().get_initial()

        if source_shopping_list.exists():
            initial['name'] = source_shopping_list.first().name
            initial['shop'] = source_shopping_list.first().shop

        return initial

    def get_context_data(self, **kwargs):
        """Load additional data to view about products and units of measurement"""
        context = super(ShoppingListCreateView, self).get_context_data(**kwargs)
        user = self.request.user
        source_slug = self.request.GET.get('source')
        source_shopping_list = ShoppingList.objects.filter(user=user, slug=source_slug)

        if source_shopping_list:
            source_shopping_list = source_shopping_list.first()
        else:
            source_shopping_list = None

        context['products_by_categories_and_favourites'] = self.get_all_products(user, source_shopping_list)
        context['UNITS_OF_MEASUREMENT'] = UNITS_OF_MEASUREMENT
        # context['source_shopping_list'] = source_shopping_list
        return context

    def form_valid(self, form):
        """Manually save data (shopping list and then products in shopping list) from form"""
        user = self.request.user
        form.instance.user = user
        try:
            products_to_save = self.get_products_for_shopping_list(user, self.request.POST)
            shopping_list = form.save()
            user_id = str(shopping_list.user_id)
            shopping_list_id = str(shopping_list.id)
            shopping_list.slug = slugify('-'.join((user_id, shopping_list_id)))
            shopping_list.save()
            self.save_products_in_shopping_list(products_to_save, shopping_list)
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


class ShoppingListUpdateView(LoginRequiredMixin, UpdateView, ShoppingListMixins):
    """Display view for editing existing shopping list"""
    success_url = reverse_lazy('shopping_list:list')
    model = ShoppingList
    form_class = CreateShoppingListForm
    template_name = 'shopping_list/create.html'

    def get_context_data(self, **kwargs):
        """Add additional data about products for selected shopping list and constant for uom"""
        context = super(ShoppingListUpdateView, self).get_context_data(**kwargs)
        user = self.request.user

        shopping_list = context['shoppinglist']

        context['products_by_categories_and_favourites'] = self.get_all_products(user, shopping_list)
        context['UNITS_OF_MEASUREMENT'] = UNITS_OF_MEASUREMENT
        return context

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super(ShoppingListUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Manually save data (shopping list and then products in shopping list) from form"""

        user = self.request.user
        form.instance.user = user
        try:
            products_to_save = self.get_products_for_shopping_list(user, self.request.POST)
            shopping_list = form.save()
            self.clear_products_in_shopping_list(shopping_list)
            self.save_products_in_shopping_list(products_to_save, shopping_list)
        except ValueError:
            return super().form_invalid(form)
        except ObjectDoesNotExist:
            return super().form_invalid(form)

        return redirect('shopping_list:list')


class ShoppingListDeleteView(LoginRequiredMixin, DeleteView):
    """Delete selected shopping list"""
    success_url = reverse_lazy('shopping_list:list')
    model = ShoppingList
    template_name = '../templates/delete_confirmation.html'
    extra_context = {'cancel_operation_url': 'shopping_list:list'}


class ShoppingListListView(LoginRequiredMixin, views.View, ShoppingListMixins):
    """Display all active shopping lists for logged user"""

    def get(self, request):
        """Get and display all active shopping lists that are owned or shared to the active user"""
        user = request.user

        shopping_lists = ShoppingList.objects.filter(Q(user=user) | Q(shared_with_list=user),
                                                     is_finished=False).order_by('-created_on')
        data_to_render = self.get_shopping_lists(shopping_lists, user)

        return render(request, 'shopping_list/main_list.html', {'data_to_render': data_to_render})


class ShoppingListUpdateProductStatus(LoginRequiredMixin, views.View):
    """Change selected product bought status on selected shopping list to opposite"""

    def post(self, request, slug, product_id):
        """Try to get requested product from selected shopping list and change it status to opposite if succeed"""
        user = request.user
        shopping_list = ShoppingList.objects.filter(user=user, slug=slug)

        if shopping_list:
            shopping_list = shopping_list.first()
            p = shopping_list.productshoppinglist_set.get(product_id=product_id)
            p.is_bought = not p.is_bought
            p.save()

        return redirect('shopping_list:list')


class ShoppingListViewComment(LoginRequiredMixin, views.View):
    """Display view with comment for selected product from selected shopping list"""

    def get(self, request, slug, product_id):
        """Try to get comment for selected product from selected shopping list and render view with it"""
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
        """Redirect to shopping list view that called comment view"""
        previous = request.POST.get('previous')
        return redirect(previous)


class ShoppingListUpdateFinishStatus(LoginRequiredMixin, views.View):
    """Change selected shopping list finished status to opposite"""
    def post(self, request, slug):
        """Try to get selected shopping list for current user and change it finished status to opposite"""
        user = request.user
        shopping_list = ShoppingList.objects.filter(user=user, slug=slug)

        if shopping_list:
            shopping_list = shopping_list.first()
            shopping_list.is_finished = not shopping_list.is_finished
            shopping_list.save()

        return redirect('shopping_list:list')


class ShoppingListHistoryListView(LoginRequiredMixin, views.View, ShoppingListMixins):
    """Display all finished shopping lists for logged user"""

    def get(self, request):
        """Get and display all finished shopping lists that are owned by the active user"""
        user = request.user

        shopping_lists = ShoppingList.objects.filter(user=user, is_finished=True).order_by('-created_on')
        data_to_render = self.get_shopping_lists(shopping_lists)

        return render(request, 'shopping_list/history_list.html', {'data_to_render': data_to_render})


class ShoppingListFavouritesListView(LoginRequiredMixin, views.View, ShoppingListMixins):
    """Display all favourite shopping lists for logged user"""

    def get(self, request):
        """Get and display all favourite shopping lists that are owned by the active user"""
        user = request.user

        shopping_lists = ShoppingList.objects.filter(user=user, is_favourite=True).order_by('created_on')
        data_to_render = self.get_shopping_lists(shopping_lists)

        return render(request, 'shopping_list/favourites_list.html', {'data_to_render': data_to_render})


class ShoppingListShareView(LoginRequiredMixin, UpdateView):
    """Display view with friends list for selecting to whom shopping list should be shared with"""
    model = ShoppingList
    fields = ('name',)
    success_url = reverse_lazy('shopping_list:list')
    template_name = 'shopping_list/friend_list.html'
    context_object_name = 'shopping_list'

    def post(self, request, *args, **kwargs):
        """Update shopping list according to selected friend to whom it should be selected"""

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

    def get_context_data(self, **kwargs):
        """Load additional data about current user friends and sharing status for selected shopping list"""
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



