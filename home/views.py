from django.shortcuts import render
from django.views import View


# Create your views here.


class HomeView(View):
    """Show home page"""
    def get(self, request):
        return render(request, 'home/home.html')
