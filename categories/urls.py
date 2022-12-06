from django.urls import path

from . import views

app_name = 'categories'

urlpatterns = [
    path('list/', views.CategoryListView.as_view(), name='list'),
    path('create/', views.CategoryCreateView.as_view(), name='create'),
    path('update/<slug:slug>', views.CategoryUpdateView.as_view(), name='update'),
    path('delete/<slug:slug>', views.CategoryDeleteView.as_view(), name='delete'),

]
