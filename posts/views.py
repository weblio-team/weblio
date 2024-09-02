from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from .models import Category, Post
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import CategoryForm, CategoryEditForm, MyPostEditForm, ToEditPostForm, MyPostAddForm
from django.db.models import Q

# views for category administrators

class CategoriesView(ListView):
    """
    Vista para listar todas las categorías en el sistema.

    Atributos:
        model (Category): El modelo que se utilizará para obtener los datos.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        ordering (list): Lista que define el orden de los resultados.
    """
    model = Category
    template_name = 'categories/categories.html'
    ordering = ['-id']


class CategoryAddView(PermissionRequiredMixin, CreateView):
    """
    Vista para crear una nueva categoría, solo accesible para usuarios con permisos específicos.

    Atributos:
        model (Category): El modelo que se utilizará para crear una nueva categoría.
        form_class (CategoryForm): El formulario que se usará para crear la categoría.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        permission_required (str): Permiso necesario para acceder a esta vista.
    """
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_add.html'
    permission_required = 'catalog.add_category'


class CategoryDetailView(DetailView):
    """
    Vista para mostrar los detalles de una categoría específica.

    Atributos:
        model (Category): El modelo que se utilizará para obtener los datos de la categoría.
        form (CategoryForm): El formulario asociado a la categoría.
        template_name (str): La plantilla que se utilizará para renderizar la vista.

    Métodos:
        get_object(): Obtiene el objeto de la categoría basado en el 'pk' y 'name'.
        get_context_data(**kwargs): Añade información adicional al contexto de la plantilla.
    """
    model = Category
    form = CategoryForm
    template_name = 'categories/category.html'

    def get_object(self):
        """Obtiene la categoría específica basada en 'pk' y 'name'."""
        pk = self.kwargs.get("pk")
        name = self.kwargs.get("name")
        return get_object_or_404(Category, pk=pk, name__iexact=name.replace('-', ' '))

    def get_context_data(self, **kwargs):
        """Añade información adicional al contexto, como el conteo total de categorías."""
        context = super().get_context_data(**kwargs)
        context['category_count'] = Category.objects.count()
        return context


class CategoryEditView(PermissionRequiredMixin, UpdateView):
    """
    Vista para editar una categoría existente, solo accesible para usuarios con permisos específicos.

    Atributos:
        model (Category): El modelo que se utilizará para editar la categoría.
        form_class (CategoryEditForm): El formulario que se usará para editar la categoría.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        permission_required (str): Permiso necesario para acceder a esta vista.
    """
    model = Category
    form_class = CategoryEditForm
    template_name = 'categories/category_edit.html'
    permission_required = 'catalog.change_category'
    
    def get_object(self):
        """Obtiene la categoría específica basada en 'pk' y 'name'."""
        pk = self.kwargs.get("pk")
        name = self.kwargs.get("name")
        return get_object_or_404(Category, pk=pk, name__iexact=name.replace('-', ' '))


class CategoryDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Vista para eliminar una categoría existente, solo accesible para usuarios con permisos específicos.

    Atributos:
        model (Category): El modelo que se utilizará para eliminar la categoría.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        success_url (str): La URL de redirección después de eliminar la categoría.
        permission_required (str): Permiso necesario para acceder a esta vista.
    """
    model = Category
    template_name = 'categories/category_delete.html'
    success_url = reverse_lazy('categories')
    permission_required = 'catalog.delete_category'

    def get_object(self):
        """Obtiene la categoría específica basada en 'pk' y 'name'."""
        pk = self.kwargs.get("pk")
        name = self.kwargs.get("name")
        return get_object_or_404(Category, pk=pk, name__iexact=name.replace('-', ' '))


# views for authors

class MyPostsView(ListView):
    """
    Vista para listar todas las publicaciones de un autor específico.

    Atributos:
        model (Post): El modelo que se utilizará para obtener los datos.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        ordering (list): Lista que define el orden de los resultados.
    """
    model = Post
    template_name = 'create/my_posts.html'
    ordering = ['-date_posted']
    
    def get_queryset(self):
        """Obtiene las publicaciones del usuario autenticado, ordenadas por fecha de publicación."""
        return Post.objects.filter(author=self.request.user).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        """Añade información adicional al contexto, como la lista de publicaciones."""
        context = super().get_context_data(**kwargs)
        context['posts'] = context['object_list']
        return context


class MyPostEditView(UpdateView):
    """
    Vista para editar una publicación existente, accesible para el autor de la publicación.

    Atributos:
        model (Post): El modelo que se utilizará para editar la publicación.
        form_class (MyPostEditForm): El formulario que se usará para editar la publicación.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        success_url (str): La URL de redirección después de editar la publicación.
    """
    model = Post
    form_class = MyPostEditForm
    template_name = 'create/edit.html'
    success_url = reverse_lazy('my-posts')

    def get_object(self, queryset=None):
        """Obtiene la publicación específica basada en 'pk'."""
        if queryset is None:
            queryset = self.get_queryset()
        
        post_id = self.kwargs.get('pk')
        post = get_object_or_404(queryset, pk=post_id)
        return post
    
    def form_valid(self, form):
        """Valida el formulario y actualiza el estado de la publicación según el botón presionado."""
        if 'status' in self.request.POST and self.request.POST['status'] == 'to_edit':
            form.instance.status = 'to_edit'
        else:
            form.instance.status = 'draft'
        return super().form_valid(form)


class MyPostDeleteView(DeleteView):
    """
    Vista para eliminar una publicación existente.

    Atributos:
        model (Post): El modelo que se utilizará para eliminar la publicación.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        success_url (str): La URL de redirección después de eliminar la publicación.
    """
    model = Post
    template_name = 'create/delete.html'
    success_url = reverse_lazy('posts')

    def get_object(self):
        """Obtiene la publicación específica basada en 'pk'."""
        pk = self.kwargs.get("pk")
        return get_object_or_404(Post, pk=pk)


class MyPostAddView(CreateView):
    """
    Vista para crear una nueva publicación.

    Atributos:
        model (Post): El modelo que se utilizará para crear la publicación.
        form_class (MyPostAddForm): El formulario que se usará para crear la publicación.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        success_url (str): La URL de redirección después de crear la publicación.
    """
    model = Post
    form_class = MyPostAddForm
    template_name = 'create/create.html'
    success_url = reverse_lazy('my-posts')

    def get_form_kwargs(self):
        """Añade el usuario autenticado a los argumentos del formulario."""
        kwargs = super(MyPostAddView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Asigna el usuario autenticado como autor de la publicación y valida el formulario."""
        form.instance.author = self.request.user
        return super(MyPostAddView, self).form_valid(form)


# views for editors

class ToEditView(ListView):
    """
    Vista para listar todas las publicaciones que necesitan edición.

    Atributos:
        model (Post): El modelo que se utilizará para obtener los datos.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        ordering (list): Lista que define el orden de los resultados.
    """
    model = Post
    template_name = 'edit/to_edit.html'
    ordering = ['-date_posted']
    
    def get_queryset(self):
        """Obtiene las publicaciones con estado 'to_edit', ordenadas por fecha de publicación."""
        return Post.objects.filter(status='to_edit').order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        """Añade información adicional al contexto, como la lista de publicaciones."""
        context = super().get_context_data(**kwargs)
        context['posts'] = context['object_list']
        return context


class ToEditPostView(UpdateView):
    """
    Vista para editar una publicación que está en proceso de edición.

    Atributos:
        model (Post): El modelo que se utilizará para editar la publicación.
        form_class (ToEditPostForm): El formulario que se usará para editar la publicación.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        success_url (str): La URL de redirección después de editar la publicación.
    """
    model = Post
    form_class = ToEditPostForm
    template_name = 'edit/edit.html'
    success_url = reverse_lazy('to-edit')

    def get_object(self, queryset=None):
        """Obtiene la publicación específica basada en 'pk'."""
        if queryset is None:
            queryset = self.get_queryset()
        
        post_id = self.kwargs.get('pk')
        post = get_object_or_404(queryset, pk=post_id)
        return post
    
    def form_valid(self, form):
        """Valida el formulario y actualiza el estado de la publicación según la entrada del usuario."""
        form.instance.status = self.request.POST.get('status')
        return super().form_valid(form)


# views for publishers

class ToPublishView(ListView):
    """
    Vista para listar todas las publicaciones que están listas para ser publicadas.

    Atributos:
        model (Post): El modelo que se utilizará para obtener los datos.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        ordering (list): Lista que define el orden de los resultados.
    """
    model = Post
    template_name = 'publish/to_publish.html'
    ordering = ['-date_posted']
    
    def get_queryset(self):
        """Obtiene las publicaciones con estado 'to_publish', ordenadas por fecha de publicación."""
        return Post.objects.filter(status='to_publish').order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        """Añade información adicional al contexto, como la lista de publicaciones."""
        context = super().get_context_data(**kwargs)
        context['posts'] = context['object_list']
        return context


class ToPublishPostView(UpdateView):
    """
    Vista para publicar una publicación, accesible solo para usuarios con permisos de publicación.

    Atributos:
        model (Post): El modelo que se utilizará para publicar la publicación.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        fields (list): Los campos que se mostrarán en el formulario.
        success_url (str): La URL de redirección después de publicar la publicación.
    """
    model = Post
    template_name = 'publish/publish.html'
    fields = '__all__'
    success_url = reverse_lazy('to-publish')

    def post(self, request, pk, *args, **kwargs):
        """Actualiza el estado de la publicación según la entrada del usuario y la guarda."""
        post = get_object_or_404(Post, pk=pk)
        status = request.POST.get('status')
        post.status = status
        post.save()
        return HttpResponseRedirect(self.success_url)


# views for subscribers

class SuscriberPostsView(ListView):
    """
    Vista para listar todas las publicaciones disponibles para suscriptores.

    Atributos:
        model (Post): El modelo que se utilizará para obtener los datos.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        ordering (list): Lista que define el orden de los resultados.
    """
    model = Post
    template_name = 'suscribers/posts.html'
    ordering = ['-date_posted']
    
    def get_queryset(self):
        """Obtiene las publicaciones con estado 'published', ordenadas por fecha de publicación."""
        return Post.objects.filter(status='published').order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        """Añade información adicional al contexto, como la lista de categorías."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class SearchPostView(ListView):
    """
    Vista para buscar publicaciones basadas en palabras clave, autor, título o categoría.

    Atributos:
        model (Post): El modelo que se utilizará para realizar la búsqueda.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        context_object_name (str): El nombre del contexto que contiene los resultados de la búsqueda.
    """
    model = Post
    template_name = 'suscribers/posts.html'
    context_object_name = 'post_search'

    def get_queryset(self):
        """Filtra las publicaciones basadas en la consulta de búsqueda proporcionada."""
        query = self.request.GET.get('q')
        if query:
            posts = Post.objects.filter(
                Q(title__iregex=query) | 
                Q(author__first_name__iregex=query) | 
                Q(author__last_name__iregex=query) | 
                Q(category__name__iregex=query) |
                Q(keywords__iregex=query)
            )
        else:
            posts = Post.objects.all()
        return posts   
    
    def get_context_data(self, **kwargs):
        """Añade información adicional al contexto, como la lista de categorías."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class SuscriberPostDetailView(DetailView):
    """
    Vista para mostrar los detalles de una publicación específica para suscriptores.

    Atributos:
        model (Post): El modelo que se utilizará para obtener los datos de la publicación.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
    
    Métodos:
        get_object(): Obtiene el objeto de la publicación basado en varios parámetros.
    """
    model = Post
    template_name = 'suscribers/post.html'

    def get_object(self):    
        """Obtiene la publicación específica basada en 'pk', 'category', 'month', 'year', y 'title'."""
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