from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from .models import Category, Post
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import CategoryForm, CategoryEditForm
from .forms import EditForm, PostForm
from django.db.models import Q

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
    
class PostsView(ListView):
    model = Post
    template_name = 'posts/posts.html'
    ordering = ['-date_posted']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class SearchPostView(ListView):
    model = Post
    template_name = 'posts/posts.html'
    context_object_name = 'post_search'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            posts = Post.objects.filter(
                Q(title__iregex=query) | 
                Q(author__first_name__iregex=query) | 
                Q(author__last_name__iregex=query) | 
                Q(category__name__iregex=query)
            )
        else:
            posts = Post.objects.all()
        return posts   
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

# clase para la vista de agregar un post
class PostAddView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_add.html'

# clase para la vista de un post en especifico
class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post.html'

    def get_object(self):    
        pk = self.kwargs.get("pk")
        category = self.kwargs.get("category")
        month = self.kwargs.get("month")
        year = self.kwargs.get("year")
        title = self.kwargs.get("title")
        return get_object_or_404(
            Post, 
            pk=pk,
            category__name__iexact=category.replace('-', ' '), 
            date_posted__month=month, 
            date_posted__year=year, 
            title__iexact=title.replace('-', ' ')
        )

# clase para la vista de editar un post
class PostEditView(UpdateView):
    model = Post
    form_class = EditForm
    template_name = 'posts/post_edit.html'

    def get_object(self):
        pk = self.kwargs.get("pk")
        category = self.kwargs.get("category")
        month = self.kwargs.get("month")
        year = self.kwargs.get("year")
        title = self.kwargs.get("title")
        return get_object_or_404(
            Post, 
            pk=pk,
            category__name__iexact=category.replace('-', ' '), 
            date_posted__month=month, 
            date_posted__year=year, 
            title__iexact=title.replace('-', ' ')
        )
# clase para la vista de eliminar un post
class PostDeleteView(DeleteView):
    model = Post
    template_name = 'posts/post_delete.html'
    success_url = reverse_lazy('posts')

    def get_object(self):
        pk = self.kwargs.get("pk")
        category = self.kwargs.get("category")
        month = self.kwargs.get("month")
        year = self.kwargs.get("year")
        title = self.kwargs.get("title")
        return get_object_or_404(
            Post, 
            pk=pk,
            category__name__iexact=category.replace('-', ' '), 
            date_posted__month=month, 
            date_posted__year=year, 
            title__iexact=title.replace('-', ' ')
        )