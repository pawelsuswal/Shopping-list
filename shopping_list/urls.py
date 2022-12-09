from django.urls import path

from . import views

app_name = 'shopping_list'

urlpatterns = [
    path('list/', views.ShoppingListListView.as_view(), name='list'),
    path('create/', views.ShoppingListCreateView.as_view(), name='create'),
    path('update/<slug:slug>', views.ShoppingListUpdateView.as_view(), name='update'),
    path('delete/<slug:slug>', views.ShoppingListDeleteView.as_view(), name='delete'),
    
]
