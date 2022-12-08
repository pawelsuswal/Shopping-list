from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView

from categories.models import Category


class CategoryCreateView(LoginRequiredMixin, CreateView):
    success_url = reverse_lazy('categories:list')
    model = Category
    fields = ('name', 'is_favourite')
    template_name = 'categories/create.html'

    # def post(self, request, *args, **kwargs):
    #     name = request.POST['name']
    #     categories = Category.objects.filter(name=name)
    #
    #     if categories:
    #         category = categories.first()
    #         category.is_active = True
    #         category.save()
    #         return redirect('categories:list')
    #
    #     return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    success_url = reverse_lazy('categories:list')
    model = Category
    fields = ('name', 'is_favourite')
    template_name = 'categories/create.html'


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('categories:list')
    model = Category
    template_name = '../templates/delete_confirmation.html'
    extra_context = {'cancel_operation_url': 'categories:list'}


class CategoryListView(LoginRequiredMixin, ListView):
    template_name = 'categories/list.html'
    model = Category
    context_object_name = 'categories'
    allow_empty = 1

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by('-is_favourite', 'name')
