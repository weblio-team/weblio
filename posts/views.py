import json
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views import View
from .models import Category, Post
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .forms import CategoryForm, CategoryEditForm, KanbanBoardForm, MyPostAddBodyForm, MyPostAddInformationForm, MyPostEditInformationForm, MyPostEditBodyForm, ToEditPostInformationForm, ToEditPostBodyForm, ToPublishPostForm
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from simple_history.utils import update_change_reason
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied
from simple_history.utils import update_change_reason


def update_change_reason(instance, reason):
    """
    Actualiza la razón de cambio para una instancia de modelo con historial.
    """
    if hasattr(instance, 'history'):
        instance.history.last().change_reason = reason
        instance.history.last().save()

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


class CategoryAddView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
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
    permission_required = 'posts.add_category'

    def form_valid(self, form):
        """Valida el formulario y guarda la nueva categoría en la base de datos."""
        messages.success(self.request, 'La categoría se ha creado correctamente.')
        return super().form_valid(form)


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
        context['posts'] = Post.objects.filter(category=self.get_object(), status='published')
        return context


class CategoryEditView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
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
    permission_required = 'posts.change_category'
    
    def get_object(self):
        """Obtiene la categoría específica basada en 'pk' y 'name'."""
        pk = self.kwargs.get("pk")
        name = self.kwargs.get("name")
        return get_object_or_404(Category, pk=pk, name__iexact=name.replace('-', ' '))
    
    def form_valid(self, form):
        """Valida el formulario y guarda los cambios en la base de datos."""
        messages.success(self.request, 'La categoría se ha actualizado correctamente.')
        return super().form_valid(form)


class CategoryDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
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
    permission_required = 'posts.delete_category'

    def get_object(self):
        """Obtiene la categoría específica basada en 'pk' y 'name'."""
        pk = self.kwargs.get("pk")
        name = self.kwargs.get("name")
        return get_object_or_404(Category, pk=pk, name__iexact=name.replace('-', ' '))
    
    def form_valid(self, form):
        """Valida el formulario y elimina la categoría de la base de datos."""
        messages.success(self.request, 'La categoría se ha eliminado correctamente.')
        return super().form_valid(form)


# views for authors

class MyPostsView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
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
    permission_required = 'posts.add_post'
    
    def get_queryset(self):
        """Obtiene las publicaciones del usuario autenticado, ordenadas por fecha de publicación."""
        return Post.objects.filter(author=self.request.user).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        """Añade información adicional al contexto, como la lista de publicaciones."""
        context = super().get_context_data(**kwargs)
        context['posts'] = context['object_list']
        return context


class MyPostEditView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    """
    Vista de edición de publicaciones personalizadas.
    MyPostEditView es una vista basada en clases que permite a los usuarios editar publicaciones existentes.
    Utiliza el modelo `Post` y renderiza la plantilla `create/edit.html`. Los campos editables incluyen 
    `título`, `etiqueta de título`, `resumen`, `cuerpo`, `categoría` y `palabras clave`.
    Métodos:
        get_context_data(self, **kwargs):
            Obtiene el contexto adicional para la plantilla, incluyendo el historial de versiones de la publicación
            y los formularios de edición. Configura la paginación para el historial de versiones.
        post(self, request, *args, **kwargs):
            Maneja la solicitud POST para actualizar la publicación. Si se solicita restaurar una versión anterior,
            inicializa los formularios con los datos de esa versión. Si no, crea los formularios con los datos 
            modificados. Guarda la publicación y registra el motivo del cambio en el historial de versiones.
    """
    model = Post
    template_name = 'create/edit.html'
    permission_required = 'posts.add_post'
    fields = ['title', 'title_tag', 'summary', 'body', 'category', 'keywords']

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if post.author != request.user:
            return HttpResponseForbidden("You are not the author of this post.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Diccionario de mapeo para traducir y formatear los estados
        state_mapping = {
            'draft': 'Borrador',
            'to_edit': 'A editar',
            'to_publish': 'A publicar',
            'published': 'Publicado',
            'inactive': 'Inactivo'
        }

        # Order version history by history_date in descending order
        post_history = post.history.order_by('-history_date')

        # Set up pagination (e.g., 5 items per page)
        paginator = Paginator(post_history, 5)  # 5 versions per page
        page = self.request.GET.get('page')

        try:
            post_history_page = paginator.page(page)
        except PageNotAnInteger:
            post_history_page = paginator.page(1)
        except EmptyPage:
            post_history_page = paginator.page(paginator.num_pages)

        context['post_history_page'] = post_history_page

        if self.request.POST:
            context['information_form'] = MyPostEditInformationForm(self.request.POST, instance=self.object)
            context['body_form'] = MyPostEditBodyForm(self.request.POST, instance=self.object)
        else:
            context['information_form'] = MyPostEditInformationForm(instance=self.object)
            context['body_form'] = MyPostEditBodyForm(instance=self.object)

        context['state_mapping'] = state_mapping
        
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Make a copy of POST data to modify
        post_data = request.POST.copy()

        if 'restore_version' in post_data:
            information_form = MyPostEditInformationForm(initial={
                'title': post_data.get('title'),
                'title_tag': post_data.get('title_tag'),
                'summary': post_data.get('summary'),
                'category': post_data.get('category'),
                'keywords': post_data.get('keywords')
            })
            body_form = MyPostEditBodyForm(initial={
                'body': post_data.get('body')
            })
        else:
            # Check if 'status' is missing and set it to the existing status from the post instance
            if 'status' not in post_data:
                post_data['status'] = self.object.status

            # Create the forms with the modified data
            information_form = MyPostEditInformationForm(post_data, instance=self.object)
            body_form = MyPostEditBodyForm(post_data, instance=self.object)

        if information_form.is_valid() and body_form.is_valid():
            post = information_form.save(commit=False)
            post.body = body_form.cleaned_data['body']

            # Check if the status has changed
            if post_data['status'] != self.object.status:
                post.status = post_data['status']
                post.change_reason = post_data.get('change_reason', 'Updated post')
            else:
                post.change_reason = post_data.get('change_reason', '')

            post.save()

            # Update the change reason in the version history
            update_change_reason(post, post.change_reason)

            messages.success(self.request, "Post saved successfully.")
            return redirect('my-posts')
        else:
            context = self.get_context_data()
            context['information_form'] = information_form
            context['body_form'] = body_form
            messages.error(self.request, 'Error al actualizar la publicación.')
            return self.render_to_response(context)

class MyPostDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
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
    permission_required = 'posts.add_post'

    def get_object(self):
        """Obtiene la publicación específica basada en 'pk'."""
        pk = self.kwargs.get("pk")
        return get_object_or_404(Post, pk=pk)
    
    def form_valid(self, form):
        """Valida el formulario y elimina la publicación de la base de datos."""
        messages.success(self.request, 'La publicación se ha eliminado correctamente.')
        return super().form_valid(form)


class MyPostAddView(PermissionRequiredMixin, LoginRequiredMixin, View):
    """
    Vista para crear una nueva publicación.

    Atributos:
        model (Post): El modelo que se utilizará para crear la publicación.
        form_class (MyPostAddForm): El formulario que se usará para crear la publicación.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        success_url (str): La URL de redirección después de crear la publicación.
    """
    permission_required = 'posts.add_post'
    def get(self, request, *args, **kwargs):
        info_form = MyPostAddInformationForm()
        body_form = MyPostAddBodyForm()
        return render(request, 'create/create.html', {
            'info_form': info_form,
            'body_form': body_form
        })

    def post(self, request, *args, **kwargs):
        info_form = MyPostAddInformationForm(request.POST)
        body_form = MyPostAddBodyForm(request.POST, request.FILES)  # For media uploads

        if info_form.is_valid() and body_form.is_valid():
            # Create the post object but don't commit it to the database yet
            post = info_form.save(commit=False)
            post.body = body_form.cleaned_data.get('body')
            post.status = 'draft'  # Set the status to 'draft'
            post.author = request.user  # Assign the current user as the author
            post.save()  # Now save the post

            return redirect('my-posts')  # Redirect to the posts list
        else:
            return render(request, 'create/create.html', {
                'info_form': info_form,
                'body_form': body_form
            })

# views for editors

class ToEditView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
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
    permission_required = 'posts.change_post'
    
    def get_queryset(self):
        """Obtiene las publicaciones con estado 'to_edit', cuyo autor no sea el usuario logueado, ordenadas por fecha de publicación."""
        return Post.objects.filter(status='to_edit').exclude(author=self.request.user).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        """Añade información adicional al contexto, como la lista de publicaciones."""
        context = super().get_context_data(**kwargs)
        context['posts'] = context['object_list']
        return context


class ToEditPostView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    """
    Vista para editar una publicación existente.
    Esta vista permite a los usuarios editar una publicación existente y ver el historial de versiones de la publicación. 
    La vista utiliza paginación para mostrar el historial de versiones y maneja formularios separados para la información 
    y el cuerpo de la publicación.
    Atributos:
        model (Post): El modelo de la publicación que se va a editar.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        fields (list): Los campos del modelo que se mostrarán en el formulario de edición.
    Métodos:
        get_context_data(**kwargs):
            Obtiene el contexto adicional para la plantilla, incluyendo el historial de versiones paginado y los formularios 
            de edición.
        post(request, *args, **kwargs):
            Maneja la solicitud POST para actualizar la publicación. Si se proporciona una versión para restaurar, 
            inicializa los formularios con los datos de esa versión. Si no, utiliza los datos proporcionados en la solicitud POST.
    """
    model = Post
    template_name = 'edit/edit.html'
    fields = ['title', 'title_tag', 'summary', 'body', 'category', 'keywords']    
    permission_required = 'posts.change_post'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if post.author == request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_history = self.object.history.all()

        # Diccionario de mapeo para traducir y formatear los estados
        state_mapping = {
            'draft': 'Borrador',
            'to_edit': 'A editar',
            'to_publish': 'A publicar',
            'published': 'Publicado',
            'inactive': 'Inactivo'
        }

        # Set up pagination (e.g., 5 items per page)
        paginator = Paginator(post_history, 5)  # 5 versions per page
        page = self.request.GET.get('page')

        try:
            post_history_page = paginator.page(page)
        except PageNotAnInteger:
            post_history_page = paginator.page(1)
        except EmptyPage:
            post_history_page = paginator.page(paginator.num_pages)

        context['post_history_page'] = post_history_page

        if self.request.POST:
            context['information_form'] = ToEditPostInformationForm(self.request.POST, instance=self.object)
            context['body_form'] = ToEditPostBodyForm(self.request.POST, instance=self.object)
        else:
            context['information_form'] = ToEditPostInformationForm(instance=self.object)
            context['body_form'] = ToEditPostBodyForm(instance=self.object)


        context['state_mapping'] = state_mapping

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Make a copy of POST data to modify
        post_data = request.POST.copy()

        if 'restore_version' in post_data:
            information_form = ToEditPostInformationForm(initial={
                'title': post_data.get('title'),
                'title_tag': post_data.get('title_tag'),
                'summary': post_data.get('summary'),
                'category': post_data.get('category'),
                'keywords': post_data.get('keywords')
            })
            body_form = ToEditPostBodyForm(initial={
                'body': post_data.get('body')
            })
            
        # Check if 'status' is missing and set it to the existing status from the post instance
        elif 'status' not in post_data:
            post_data['status'] = self.object.status

        # Create the forms with the modified data
        information_form = ToEditPostInformationForm(post_data, instance=self.object)
        body_form = ToEditPostBodyForm(post_data, instance=self.object)

        if information_form.is_valid() and body_form.is_valid():
            post = information_form.save(commit=False)
            body_form.save(commit=False)

            # Obtener la razón de cambio y el estado
            change_reason = post_data.get('change_reason', '')
            status = post_data.get('status', '')

            # Check if the status has changed
            if post_data['status'] != self.object.status:
                post.status = post_data['status']
                post.change_reason = post_data.get('change_reason', 'Updated post')
            else:
                post.change_reason = post_data.get('change_reason', '')

            post.save()

            return redirect('to-edit')
        else:
            context = self.get_context_data()
            context['information_form'] = information_form
            context['body_form'] = body_form
            return self.render_to_response(context)
        
    def form_valid(self, form):
        """Valida el formulario y actualiza el estado de la publicación según la entrada del usuario."""
        information_form = ToEditPostInformationForm(self.request.POST, instance=self.object)
        body_form = ToEditPostBodyForm(self.request.POST, instance=self.object)
        
        self.object = information_form.save(commit=False)
        body_form.save(commit=False)
        change_reason = self.request.POST.get('change_reason', '')
        status = self.request.POST.get('status', '')
        if change_reason:
            update_change_reason(self.object, change_reason)
        if status:
            self.object.status = status
        self.object.save()
        body_form.save()
        return HttpResponseRedirect(self.get_success_url())
    


# views for publishers

class ToPublishView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
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
    permission_required = 'posts.can_publish'
    
    def get_queryset(self):
        """Obtiene las publicaciones con estado 'to_publish', cuyo autor no sea el usuario logueado, ordenadas por fecha de publicación."""
        return Post.objects.filter(status='to_publish').exclude(author=self.request.user).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        """Añade información adicional al contexto, como la lista de publicaciones."""
        context = super().get_context_data(**kwargs)
        context['posts'] = context['object_list']
        return context


class ToPublishPostView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
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
    success_url = reverse_lazy('to-publish')
    permission_required = 'posts.can_publish'
    form_class = ToPublishPostForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        post_history = post.history.order_by('-history_date')

        # Set up pagination (e.g., 5 items per page)
        paginator = Paginator(post_history, 5)  # 5 versions per page
        page = self.request.GET.get('page')

        try:
            post_history_page = paginator.page(page)
        except PageNotAnInteger:
            post_history_page = paginator.page(1)
        except EmptyPage:
            post_history_page = paginator.page(paginator.num_pages)

        # Diccionario de mapeo para traducir y formatear los estados
        state_mapping = {
            'draft': 'Borrador',
            'to_edit': 'A editar',
            'to_publish': 'A publicar',
            'published': 'Publicado',
            'inactive' : 'Inactivo'
        }

        context['post_history_page'] = post_history_page
        context['state_mapping'] = state_mapping
        return context

    def post(self, request, *args, **kwargs):
        """Actualiza el estado de la publicación según la entrada del usuario y la guarda."""
        self.object = self.get_object()
        post_data = request.POST.copy()

        form = ToPublishPostForm(post_data, instance=self.object)

        if form.is_valid():
            post = form.save(commit=False)

            # Obtener la razón de cambio y el estado
            change_reason = post_data.get('change_reason', '')
            status = post_data.get('status', '')

            if post_data['status'] != self.object.status:
                post.status = post_data['status']
                post.change_reason = post_data.get('change_reason', 'Updated post')
            else:
                post.change_reason = post_data.get('change_reason', '')

            post.save()

            return redirect('to-publish')
        else:
            context = self.get_context_data(form=form)
            return self.render_to_response(context)
        
    def form_valid(self, form):
        """Valida el formulario y actualiza el estado de la publicación según la entrada del usuario."""
        form = ToPublishPostForm(self.request.POST, instance=self.object)

        self.object = form.save(commit=False)
        change_reason = self.request.POST.get('change_reason', '')
        status = self.request.POST.get('status', '')
        if change_reason:
            update_change_reason(self.object, change_reason)
        if status:
            self.object.status = status
        self.object.save()
        form.save()
        return HttpResponseRedirect(self.get_success_url())

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
        # Obtener la hora actual en UTC
        now = timezone.now()
        
        # Condición 1: Si publish_start_date y publish_end_date no son nulos y la fecha actual está en el rango
        programmed = Q(publish_start_date__lte=now, publish_end_date__gte=now, publish_start_date__isnull=False, publish_end_date__isnull=False)

        # Condición 2: Si publish_start_date y publish_end_date son nulos
        regular = Q(publish_start_date__isnull=True, publish_end_date__isnull=True)

        # Filtrar los posts con status 'published' que cumplan cualquiera de las dos condiciones
        return Post.objects.filter(
            Q(status='published') & (programmed | regular)
        ).order_by('-date_posted')
    
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
        dispatch(): Realiza validaciones antes de procesar la solicitud.
        get_object(): Obtiene el objeto de la publicación basado en varios parámetros.
    """
    model = Post
    template_name = 'suscribers/post.html'

    def dispatch(self, request, *args, **kwargs):
        """Realiza validaciones antes de procesar la solicitud."""
        pk = self.kwargs.get("pk")
        category = self.kwargs.get("category")
        month = self.kwargs.get("month")
        year = self.kwargs.get("year")
        title = self.kwargs.get("title")
        post = get_object_or_404(
            Post, 
            pk=pk,
            category__name__iexact=category.replace('-', ' '), 
            date_posted__month=month, 
            date_posted__year=year, 
            title__iexact=title.replace('-', ' ')
        )

        if request.user.is_anonymous and post.category.kind != 'public':
            messages.warning(request, "Debe registrarse para ver publicaciones para suscriptores.")
            return redirect(reverse_lazy('posts'))  # Reemplaza 'home' con el nombre de tu URL de inicio

        return super().dispatch(request, *args, **kwargs)

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
    


class KanbanBoardView(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    """
    Una vista para mostrar un tablero Kanban.
    Esta vista extiende la clase TemplateView y renderiza la plantilla 'kanban/kanban_board.html'.
    Proporciona los siguientes datos de contexto a la plantilla:
    - 'draft_posts': Un queryset de objetos Post con status='draft'.
    - 'to_edit_posts': Un queryset de objetos Post con status='to_edit'.
    - 'to_publish_posts': Un queryset de objetos Post con status='to_publish'.
    - 'published_posts': Un queryset de objetos Post con status='published'.
    - 'form': Una instancia de KanbanBoardForm.
    La vista también maneja las solicitudes POST. Si el formulario es válido, guarda los datos del formulario y redirige
    al usuario a la URL 'kanban-board'. Si el formulario no es válido, vuelve a renderizar la vista con el
    formulario y los datos de contexto existentes.
    """
    template_name = 'kanban/kanban_board.html'
    permission_required = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Check user permissions
        can_create = user.has_perm('posts.add_post')
        can_edit = user.has_perm('posts.change_post')
        can_publish = user.has_perm('posts.can_publish')

        if can_create and not can_edit and not can_publish:
            # User can only create posts, show only their posts
            draft_posts = Post.objects.filter(status='draft', author=user)
            to_edit_posts = Post.objects.filter(status='to_edit', author=user)
            to_publish_posts = Post.objects.filter(status='to_publish', author=user)
            published_posts = Post.objects.filter(status='published', author=user)
        else:
            # User has other permissions, show all posts
            draft_posts = Post.objects.filter(status='draft')
            to_edit_posts = Post.objects.filter(status='to_edit')
            to_publish_posts = Post.objects.filter(status='to_publish')
            published_posts = Post.objects.filter(status='published')

        context.update({
            'draft_posts': draft_posts,
            'to_edit_posts': to_edit_posts,
            'to_publish_posts': to_publish_posts,
            'published_posts': published_posts,
            'form': KanbanBoardForm(),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        form = KanbanBoardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kanban-board')
        return self.get(request, *args, **kwargs)
    


@method_decorator(csrf_exempt, name='dispatch')
class UpdatePostsStatusView(PermissionRequiredMixin, LoginRequiredMixin, View):
    """
    Vista para actualizar el estado de los articulos.

    Esta vista se encarga de recibir una solicitud POST con datos en formato JSON.
    Los datos deben contener una lista de articulos movidos, donde cada elemento
    de la lista debe tener el ID de articulo y el ID del nuevo estado.

    Si el articulo existe, se actualiza su estado con el nuevo ID proporcionado.
    Si el articulo no existe, se ignora y se continúa con los demás articulos.

    La vista devuelve una respuesta JSON indicando si la actualización fue exitosa o no.

    Atributos:
        - csrf_exempt: Decorador para eximir la vista de la protección CSRF.

    Métodos:
        - post: Método que maneja la solicitud POST y actualiza los estados de los articulos.

    Parámetros de la solicitud:
        - request: La solicitud HTTP recibida.
        - args: Argumentos posicionales adicionales.
        - kwargs: Argumentos de palabras clave adicionales.

    Excepciones:
        - Post.DoesNotExist: Se produce si una publicación no existe en la base de datos.

    Retorno:
        - JsonResponse: Respuesta JSON indicando si la actualización fue exitosa o no.
    """
    
    permission_required = []

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            movedPosts = data.get('movedPosts', [])
            for item in movedPosts:
                post_id = item.get('post_id')
                status_id = item.get('status_id')
                try:
                    post = Post.objects.get(pk=post_id)
                    post.status = status_id
                    post.save()
                except Post.DoesNotExist:
                    pass
            messages.success(request, 'Los estados de las publicaciones se han actualizado correctamente.')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        

class HistoryView(DetailView):
    """
    Vista para mostrar el historial de un post específico.

    Atributos:
        model (Post): El modelo que se utilizará para obtener los datos del post.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
    """
    model = Post
    template_name = 'history/history_detail.html'

    def get_object(self):
        post_pk = self.kwargs.get('pk')
        history_id = self.kwargs.get('history_id')
        post = get_object_or_404(Post, pk=post_pk)
        
        try:
            history_instance = post.history.get(history_id=history_id)
        except post.history.model.DoesNotExist:
            raise Http404("No HistoricalPost matches the given query.")
        
        return history_instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['post_pk'] = self.kwargs.get('pk')
        return context