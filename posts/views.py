from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from .models import Category
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import CategoryForm, CategoryEditForm

# Create your views here.
class HomeView(ListView):
    model = Category
    template_name = 'categories/home.html'
    
class CategoriesView(ListView):
    model = Category
    template_name = 'categories/categories.html'
    ordering = ['-id']

class CategoryAddView(PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_add.html'
    permission_required = 'catalog.add_category'

class CategoryDetailView(DetailView):
    model = Category
    form = CategoryForm
    template_name = 'categories/category.html'

    def get_object(self):
        pk = self.kwargs.get("pk")
        name = self.kwargs.get("name")
        return get_object_or_404(Category, pk=pk, name__iexact=name.replace('-', ' '))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_count'] = Category.objects.count()
        return context

class CategoryEditView(PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryEditForm
    template_name = 'categories/category_edit.html'
    permission_required = 'catalog.change_category'
    
    def get_object(self):
        pk = self.kwargs.get("pk")
        name = self.kwargs.get("name")
        return get_object_or_404(Category, pk=pk, name__iexact=name.replace('-', ' '))

class CategoryDeleteView(PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'categories/category_delete.html'
    success_url = reverse_lazy('categories')
    permission_required = 'catalog.delete_category'

    def get_object(self):
        pk = self.kwargs.get("pk")
        name = self.kwargs.get("name")
        return get_object_or_404(Category, pk=pk, name__iexact=name.replace('-', ' '))