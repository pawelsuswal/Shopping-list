from django.urls import path

from . import views

app_name = 'shopping_list'

urlpatterns = [
    path('list/', views.ShoppingListListView.as_view(), name='list'),
    path('list/history/', views.ShoppingListHistoryListView.as_view(), name='history'),
    path('list/favourites/', views.ShoppingListFavouritesListView.as_view(), name='favourites'),
    path('create/', views.ShoppingListCreateView.as_view(), name='create'),
    path('update/<slug:slug>', views.ShoppingListUpdateView.as_view(), name='update'),
    path('update/<slug:slug>/<int:product_id>',
         views.ShoppingListUpdateProductStatus.as_view(),
         name='change_product_status'),
    path('update/finish/<slug:slug>', views.ShoppingListUpdateFinishStatus.as_view(), name='change_finish_status'),
    path('delete/<slug:slug>', views.ShoppingListDeleteView.as_view(), name='delete'),
    path('share/<slug>', views.ShoppingListShareView.as_view(), name='share'),
    path('view/comment/<slug:slug>/<int:product_id>',
         views.ShoppingListViewComment.as_view(),
         name='view_comment'),

]
