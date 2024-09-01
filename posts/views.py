from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from .models import Category, Post
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import CategoryForm, CategoryEditForm
from .forms import MyPostEditForm, ToEditPostForm
from .models import Post

from .forms import MyPostAddForm
from django.db.models import Q

# views for category administrators
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

# views for authors
class MyPostsView(ListView):
    model = Post
    template_name = 'create/my_posts.html'
    ordering = ['-date_posted']
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = context['object_list']
        return context

class MyPostEditView(UpdateView):
    model = Post
    form_class = MyPostEditForm
    template_name = 'create/edit.html'
    success_url = reverse_lazy('my-posts')

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        post_id = self.kwargs.get('pk')
        post = get_object_or_404(queryset, pk=post_id)
        return post
    
    def form_valid(self, form):
        status = self.request.POST.get('status')
        print(status)
        if status == 'draft':
            form.instance.status = 'to_edit'
        return super().form_valid(form)

class MyPostDeleteView(DeleteView):
    model = Post
    template_name = 'create/delete.html'
    success_url = reverse_lazy('posts')

    def get_object(self):
        pk = self.kwargs.get("pk")
        return get_object_or_404(
            Post, 
            pk=pk,
        )

class MyPostAddView(CreateView):
    model = Post
    form_class = MyPostAddForm
    template_name = 'create/create.html'

# views for editors
class ToEditView(ListView):
    model = Post
    template_name = 'edit/to_edit.html'
    ordering = ['-date_posted']
    
    def get_queryset(self):
        return Post.objects.filter(status='to_edit').order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = context['object_list']
        return context

class ToEditPostView(UpdateView):
    model = Post
    form_class = ToEditPostForm
    template_name = 'edit/edit.html'
    success_url = reverse_lazy('to-edit')

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        post_id = self.kwargs.get('pk')
        post = get_object_or_404(queryset, pk=post_id)
        return post
    
    def form_valid(self, form):
        form.instance.status = self.request.POST.get('status')
        return super().form_valid(form)
    
# views for publishers  
class ToPublishView(ListView):
    model = Post
    template_name = 'publish/to_publish.html'
    ordering = ['-date_posted']
    
    def get_queryset(self):
        return Post.objects.filter(status='to_publish').order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = context['object_list']
        return context

class ToPublishPostView(UpdateView):
    model = Post
    template_name = 'publish/publish.html'
    fields = '__all__'
    success_url = reverse_lazy('to-publish')

    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        status = request.POST.get('status')
        post.status = status

        post.save()
        return HttpResponseRedirect(self.success_url)
    
# views for suscribers
class SuscriberPostsView(ListView):
    model = Post
    template_name = 'suscribers/posts.html'
    ordering = ['-date_posted']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class SearchPostView(ListView):
    model = Post
    template_name = 'suscribers/posts.html'
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

class SuscriberPostDetailView(DetailView):
    model = Post
    template_name = 'suscribers/post.html'

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