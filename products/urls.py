from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('list/', views.ProductListView.as_view(), name='list'),
    path('create/', views.ProductCreateView.as_view(), name='create'),
    path('update/<slug:slug>', views.ProductUpdateView.as_view(), name='update'),
    path('delete/<slug:slug>', views.ProductDeleteView.as_view(), name='delete'),
]
