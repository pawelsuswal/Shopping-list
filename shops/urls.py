from django.urls import path

from . import views

app_name = 'shops'

urlpatterns = [
    path('list/', views.ShopListView.as_view(), name='list'),
    path('create/', views.ShopCreateView.as_view(), name='create'),
    path('update/<slug:slug>', views.ShopUpdateView.as_view(), name='update'),
    path('delete/<slug:slug>', views.ShopDeleteView.as_view(), name='delete'),
    path('reorder/<slug:slug>/<int:category>', views.ShopCategoriesReorderedView.as_view(), name='reorder'),
    path('reorder/<slug:slug>', views.ShopCategoriesReorderedView.as_view(), name='reorder'),

]
