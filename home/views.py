from django.shortcuts import render
from django.views import View

from categories.models import Category
from products.models import Product
from shops.models import Shop


# Create your views here.


class HomeView(View):
    """Show home page"""
    def get(self, request):
        user = request.user
        context = {}
        if user.is_authenticated:
            if not Category.objects.filter(user=user):
                context['dont_have_categories'] = True
            if not Shop.objects.filter(user=user):
                context['dont_have_shops'] = True
            if not Product.objects.filter(user=user):
                context['dont_have_products'] = True

        return render(request, 'home/home.html', context)
