import json
from django.db import IntegrityError
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views import View
from .models import Category, Post, Report, Member
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .forms import CategoryForm, CategoryEditForm, KanbanBoardForm, MyPostAddBodyForm, MyPostAddGeneralForm, MyPostAddProgramForm, MyPostAddThumbnailForm, MyPostEditGeneralForm, MyPostEditBodyForm, MyPostEditProgramForm, MyPostEditThumbnailForm, ToEditPostGeneralForm, ToEditPostBodyForm, ToPublishPostForm
from django.db.models import Q, OuterRef, Subquery, Count
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied
from django.conf import settings
from .forms import ReportForm
from django.utils.text import slugify
from django.db.models import Count

from simple_history.utils import update_change_reason
import random
from django.core.files.storage import default_storage
from datetime import timedelta


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
        context['DEBUG'] = settings.DEBUG
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
    permission_required = 'posts.add_post'
    
    def get_queryset(self):
        """Obtiene las publicaciones del usuario autenticado, ordenadas por la fecha de la última versión del historial donde el autor es el history_user."""
        PostHistory = Post.history.model
        latest_history = PostHistory.objects.filter(
            id=OuterRef('id'),
            history_user=self.request.user
        ).order_by('-history_date')
        
        queryset = Post.objects.filter(author=self.request.user).annotate(
            latest_history_date=Subquery(latest_history.values('history_date')[:1])
        ).order_by('-latest_history_date')
        
        return queryset
    
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
    fields = ['title', 'title_tag', 'summary', 'body', 'category', 'keywords', 'publish_start_date', 'publish_end_date', 'thumbnail']

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
        post_history_with_reason = post.history.filter(change_reason__isnull=False).exclude(change_reason='').order_by('-history_date')

        # Set up pagination (e.g., 5 items per page)
        paginator = Paginator(post_history, 5)
        paginator_with_reason = Paginator(post_history_with_reason, 5)

        page = self.request.GET.get('page')
        page_with_reason = self.request.GET.get('page_with_reason')

        try:
            post_history_page = paginator.page(page)
        except PageNotAnInteger:
            post_history_page = paginator.page(1)
        except EmptyPage:
            post_history_page = paginator.page(paginator.num_pages)

        try:
            post_history_with_reason_page = paginator_with_reason.page(page_with_reason)
        except PageNotAnInteger:
            post_history_with_reason_page = paginator_with_reason.page(1)
        except EmptyPage:
            post_history_with_reason_page = paginator_with_reason.page(paginator_with_reason.num_pages)

        context['post_history_page'] = post_history_page
        context['post_history_with_reason_page'] = post_history_with_reason_page
        
        # Obtener la versión específica de la imagen si se solicita restaurar
        if self.request.POST.get('operation') == 'restore':
            post_version = get_object_or_404(get_object_or_404(Post, pk=self.request.POST.get('post_id')).history, pk=self.request.POST.get('history_id'))
            context['current_thumbnail_url'] = default_storage.url(post_version.thumbnail)
            context['post_id'] = self.request.POST.get('post_id')
            context['history_id'] = self.request.POST.get('history_id')
        # Si no se solicita restaurar una versión anterior, mostrar la imagen actual del objeto
        else:
            context['current_thumbnail_url'] = post.thumbnail.url if post.thumbnail else None

        if self.request.POST:
            context['gen_form'] = MyPostEditGeneralForm(self.request.POST, instance=post)
            context['body_form'] = MyPostEditBodyForm(self.request.POST, instance=post)
            context['thumbnail_form'] = MyPostEditThumbnailForm(self.request.POST, self.request.FILES, instance=post)
            context['program_form'] = MyPostEditProgramForm(self.request.POST, instance=post)  # Faltaba instance=post
        else:
            context['gen_form'] = MyPostEditGeneralForm(instance=post)            
            context['body_form'] = MyPostEditBodyForm(instance=post)
            context['thumbnail_form'] = MyPostEditThumbnailForm(instance=post)
            context['program_form'] = MyPostEditProgramForm(instance=post)  # Faltaba instance=post
            context['gen_form'].fields['category'].queryset = Category.objects.all() if self.request.user.has_perm('members.auto_publish') else Category.objects.filter(moderated=True)

        context['categories_json'] = json.dumps(list(Category.objects.values('id', 'name', 'moderated')))  
        context['state_mapping'] = state_mapping
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Make a copy of POST data to modify
        post_data = request.POST.copy()

        # Initialize forms
        gen_form = None
        body_form = None
        thumbnail_form = None
        program_form = None

        # Comprobar si se solicita restaurar una versión anterior
        if post_data.get('operation') == 'restore':
            post_version = get_object_or_404(get_object_or_404(Post, pk=post_data.get('post_id')).history, pk=post_data.get('history_id'))
            
            gen_form = MyPostEditGeneralForm(initial={
                'title': post_version.title,
                'title_tag': post_version.title_tag,
                'summary': post_version.summary,
                'category': post_version.category.name,
                'keywords': post_version.keywords,
            })
            body_form = MyPostEditBodyForm(initial={
                'body': post_version.body
            })
            program_form = MyPostEditProgramForm(initial={
                'publish_start_date': post_version.publish_start_date,
                'publish_end_date': post_version.publish_end_date
            })
            thumbnail_form = MyPostEditThumbnailForm(initial={
                'thumbnail': post_version.thumbnail
            })
        
        # Si no se solicita restaurar una versión anterior o se está guardando una nueva versión o se está guardando una versión anterior
        else:
            # Check if 'status' is missing and set it to the existing status from the post instance
            if 'status' not in post_data:
                post_data['status'] = self.object.status

            # Create the forms with the modified data
            gen_form = MyPostEditGeneralForm(post_data, instance=self.object)
            body_form = MyPostEditBodyForm(post_data, instance=self.object)

            # Comprobar si se está restaurando una versión anterior
            if post_data.get('post_id') != '' and post_data.get('history_id') != '':  # Si se está restaurando una versión anterior
                post_version = get_object_or_404(get_object_or_404(Post, pk=post_data.get('post_id')).history, pk=post_data.get('history_id'))
                self.object.thumbnail = post_version.thumbnail
            if post_data.get('thumbnail') == 'None': self.object.thumbnail = None # Si se elimina la imagen
            thumbnail_form = MyPostEditThumbnailForm(post_data, request.FILES, instance=self.object)
            program_form = MyPostEditProgramForm(post_data, instance=self.object)

        # si se esta guardando una nueva version
        if gen_form.is_valid() and body_form.is_valid() and thumbnail_form.is_valid() and program_form.is_valid():
            post = gen_form.save(commit=False)
            post.body = body_form.cleaned_data['body']
            post.thumbnail = thumbnail_form.cleaned_data.get('thumbnail')
            post.publish_start_date = program_form.cleaned_data.get('publish_start_date')
            post.publish_end_date = program_form.cleaned_data.get('publish_end_date')

            # Check if the status has changed
            if post_data['status'] != self.object.status:
                post.status = post_data['status']
                post.change_reason = post_data.get('change_reason', 'Updated post')
            else:
                post.change_reason = post_data.get('change_reason', '')

            post.save()

            # Update the change reason in the version history
            update_change_reason(post, post.change_reason)

            messages.success(self.request, "El artículo se ha actualizado correctamente.")
            return redirect('my-posts')
        # si se esta restaurando a una version anterior
        else:
            context = self.get_context_data()
            context['gen_form'] = gen_form
            context['body_form'] = body_form
            context['thumbnail_form'] = thumbnail_form
            context['program_form'] = program_form
            messages.success(self.request, 'El artículo se ha restaurado correctamente.')
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
        gen_form = MyPostAddGeneralForm()
        body_form = MyPostAddBodyForm()
        thumbnail_form = MyPostAddThumbnailForm()
        program_form = MyPostAddProgramForm()
        gen_form.fields['category'].queryset = Category.objects.all() if self.request.user.has_perm('members.auto_publish') else Category.objects.filter(moderated=True)
        return render(request, 'create/create.html', {
            'gen_form': gen_form,
            'body_form': body_form,
            'thumbnail_form': thumbnail_form,
            'program_form': program_form,
        })

    def post(self, request, *args, **kwargs):
        gen_form = MyPostAddGeneralForm(request.POST)
        thumbnail_form = MyPostAddThumbnailForm(request.POST, request.FILES)  # For media uploads
        program_form = MyPostAddProgramForm(request.POST)
        body_form = MyPostAddBodyForm(request.POST, request.FILES)  # For media uploads

        if gen_form.is_valid() and body_form.is_valid() and thumbnail_form.is_valid() and program_form.is_valid():
            # Create the post object but don't commit it to the database yet
            post = gen_form.save(commit=False)
            post.body = body_form.cleaned_data.get('body')
            post.status = 'draft'  # Set the status to 'draft'
            post.author = request.user  # Assign the current user as the author
            post.thumbnail = thumbnail_form.cleaned_data.get('thumbnail')
            post.publish_start_date = program_form.cleaned_data.get('publish_start_date')
            post.publish_end_date = program_form.cleaned_data.get('publish_end_date')
            post.save()  # Now save the post

            return redirect('my-posts')  # Redirect to the posts list
        else:
            return render(request, 'create/create.html', {
                'gen_form': gen_form,
                'body_form': body_form,
                'thumbnail_form': thumbnail_form,
                'program_form': program_form,
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
    permission_required = 'posts.change_post'
    
    def get_queryset(self):
        """Obtiene las publicaciones con estado 'to_edit', cuyo autor no sea el usuario logueado, ordenadas por la fecha de la última versión del historial."""
        PostHistory = Post.history.model
        latest_history = PostHistory.objects.filter(id=OuterRef('id')).order_by('-history_date')
        
        queryset = Post.objects.filter(status='to_edit').exclude(author=self.request.user).annotate(
            latest_history_date=Subquery(latest_history.values('history_date')[:1])
        ).order_by('-latest_history_date')
        
        return queryset
    
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
    permission_required = 'posts.change_post'
    fields = ['title', 'title_tag', 'summary', 'body', 'category', 'keywords', 'publish_start_date', 'publish_end_date', 'thumbnail']

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if post.author == request.user:
            raise PermissionDenied
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
        post_history_with_reason = post.history.filter(change_reason__isnull=False).exclude(change_reason='').order_by('-history_date')

        # Set up pagination (e.g., 5 items per page)
        paginator = Paginator(post_history, 5)
        paginator_with_reason = Paginator(post_history_with_reason, 5)

        page = self.request.GET.get('page')
        page_with_reason = self.request.GET.get('page_with_reason')

        try:
            post_history_page = paginator.page(page)
        except PageNotAnInteger:
            post_history_page = paginator.page(1)
        except EmptyPage:
            post_history_page = paginator.page(paginator.num_pages)

        try:
            post_history_with_reason_page = paginator_with_reason.page(page_with_reason)
        except PageNotAnInteger:
            post_history_with_reason_page = paginator_with_reason.page(1)
        except EmptyPage:
            post_history_with_reason_page = paginator_with_reason.page(paginator_with_reason.num_pages)

        context['post_history_page'] = post_history_page
        context['post_history_with_reason_page'] = post_history_with_reason_page

        # Obtener la versión específica de la imagen si se solicita restaurar
        if self.request.POST.get('operation') == 'restore':
            post_version = get_object_or_404(get_object_or_404(Post, pk=self.request.POST.get('post_id')).history, pk=self.request.POST.get('history_id'))
            context['current_thumbnail_url'] = default_storage.url(post_version.thumbnail)
            context['post_id'] = self.request.POST.get('post_id')
            context['history_id'] = self.request.POST.get('history_id')
            context['publish_start_date'] = post_version.publish_start_date
            context['publish_end_date'] = post_version.publish_end_date
        # Si no se solicita restaurar una versión anterior, mostrar la imagen y la fecha programada actual del objeto
        else:
            context['current_thumbnail_url'] = post.thumbnail.url if post.thumbnail else None
            context['publish_start_date'] = self.object.publish_start_date
            context['publish_end_date'] = self.object.publish_end_date

        if self.request.POST:
            context['gen_form'] = MyPostEditGeneralForm(self.request.POST, instance=post)
            context['body_form'] = MyPostEditBodyForm(self.request.POST, instance=post)
            context['thumbnail_form'] = MyPostEditThumbnailForm(self.request.POST, self.request.FILES, instance=post)
            context['program_form'] = MyPostEditProgramForm(self.request.POST, instance=post)  # Faltaba instance=post
        
        else:
            context['gen_form'] = MyPostEditGeneralForm(instance=post)
            context['body_form'] = MyPostEditBodyForm(instance=post)
            context['thumbnail_form'] = MyPostEditThumbnailForm(instance=post)
            context['program_form'] = MyPostEditProgramForm(instance=post)  # Faltaba instance=post

        context['state_mapping'] = state_mapping
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Make a copy of POST data to modify
        post_data = request.POST.copy()

        # Initialize forms
        gen_form = None
        body_form = None
        thumbnail_form = None
        program_form = None

        # Comprobar si se solicita restaurar una versión anterior
        if post_data.get('operation') == 'restore':
            post_version = get_object_or_404(get_object_or_404(Post, pk=post_data.get('post_id')).history, pk=post_data.get('history_id'))
            gen_form = MyPostEditGeneralForm(initial={
                'title': post_version.title,
                'title_tag': post_version.title_tag,
                'summary': post_version.summary,
                'category': post_version.category.name,
                'keywords': post_version.keywords,
            })
            body_form = MyPostEditBodyForm(initial={
                'body': post_version.body
            })
            program_form = MyPostEditProgramForm(initial={
                'publish_start_date': post_version.publish_start_date,
                'publish_end_date': post_version.publish_end_date
            })
            thumbnail_form = MyPostEditThumbnailForm(initial={
                'thumbnail': post_version.thumbnail
            })
        
        # Si no se solicita restaurar una versión anterior o se está guardando una nueva versión o se está guardando una versión anterior
        else:
            # Check if 'status' is missing and set it to the existing status from the post instance
            if 'status' not in post_data:
                post_data['status'] = self.object.status

            # Create the forms with the modified data
            gen_form = MyPostEditGeneralForm(post_data, instance=self.object)
            body_form = MyPostEditBodyForm(post_data, instance=self.object)

            # Comprobar si se está restaurando una versión anterior
            if post_data.get('post_id') != '' and post_data.get('history_id') != '':  # Si se está restaurando una versión anterior
                post_version = get_object_or_404(get_object_or_404(Post, pk=post_data.get('post_id')).history, pk=post_data.get('history_id'))
                self.object.thumbnail = post_version.thumbnail
                self.object.publish_start_date = post_version.publish_start_date
                self.object.publish_end_date = post_version.publish_end_date
            thumbnail_form = MyPostEditThumbnailForm(post_data, request.FILES, instance=self.object)
            program_form = MyPostEditProgramForm(post_data, instance=self.object)

        # si se esta guardando una nueva version
        if gen_form.is_valid() and body_form.is_valid() and thumbnail_form.is_valid() and program_form.is_valid():
            post = gen_form.save(commit=False)
            post.body = body_form.cleaned_data.get('body')
              
            if post_data.get('history_id') != '':  # Si se está restaurando una versión anterior
                post_version = get_object_or_404(get_object_or_404(Post, pk=post_data.get('post_id')).history, pk=post_data.get('history_id'))
                post.publish_start_date = post_version.publish_start_date
                post.publish_end_date = post_version.publish_end_date
            else:
                post_version = get_object_or_404(Post, pk=post_data.get('post_id'))
                post.publish_start_date = post_version.publish_start_date
                post.publish_end_date = post_version.publish_end_date
            
            post.thumbnail = thumbnail_form.cleaned_data.get('thumbnail')
            # Check if the status has changed
            if post_data['status'] != self.object.status:
                post.status = post_data['status']
                post.change_reason = post_data.get('change_reason', 'Updated post')
            else:
                post.change_reason = post_data.get('change_reason', '')

            post.save()

            # Update the change reason in the version history
            update_change_reason(post, post.change_reason)
            messages.success(self.request, "El artículo se ha actualizado correctamente.")
            return redirect('to-edit')
        # si se esta restaurando a una version anterior
        else:
            context = self.get_context_data()
            context['gen_form'] = gen_form
            context['body_form'] = body_form
            context['thumbnail_form'] = thumbnail_form
            context['program_form'] = program_form
            messages.success(self.request, 'El artículo se ha restaurado correctamente.')
            return self.render_to_response(context)
        
    def form_valid(self, form):
        """Valida el formulario y actualiza el estado de la publicación según la entrada del usuario."""
        gen_form = ToEditPostGeneralForm(self.request.POST, instance=self.object)
        body_form = ToEditPostBodyForm(self.request.POST, instance=self.object)

        if gen_form.is_valid() and body_form.is_valid():
            self.object = gen_form.save(commit=False)
            self.object.body = body_form.cleaned_data['body']

            change_reason = self.request.POST.get('change_reason', '')
            status = self.request.POST.get('status', '')

            if change_reason:
                update_change_reason(self.object, change_reason)
            if status:
                self.object.status = status

            self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            context = self.get_context_data()
            context['gen_form'] = gen_form
            context['body_form'] = body_form
            return self.render_to_response(context)
    


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
    permission_required = 'posts.can_publish'
    
    def get_queryset(self):
        """Obtiene las publicaciones con estado 'to_publish', cuyo autor no sea el usuario logueado, ordenadas por la fecha de la última versión del historial."""
        PostHistory = Post.history.model
        latest_history = PostHistory.objects.filter(id=OuterRef('id')).order_by('-history_date')
        
        queryset = Post.objects.filter(status='to_publish').exclude(author=self.request.user).annotate(
            latest_history_date=Subquery(latest_history.values('history_date')[:1])
        ).order_by('-latest_history_date')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Añade información adicional al contexto, como la lista de publicaciones y las fechas de publicación."""
        context = super().get_context_data(**kwargs)
        context['posts'] = context['object_list']
        
        # Añadir las fechas de publicación al contexto
        publish_dates = {}
        for post in context['posts']:
            publish_dates[post.id] = {
                'publish_start_date': post.publish_start_date,
                'publish_end_date': post.publish_end_date
            }
        context['publish_dates'] = publish_dates
        
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
        post_history = self.object.history.filter(change_reason__isnull=False).exclude(change_reason='')

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
        context['publish_start_date'] = post.publish_start_date
        context['publish_end_date'] = post.publish_end_date
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

            # Si el estado es 'published', establecer las fechas de publicación si no están definidas
            if post.publish_start_date is None:
                post.publish_start_date = timezone.now()
                post.publish_end_date = timezone.now() + timedelta(days=7)

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

class SuscriberExplorePostsView(ListView):
    """
    Vista para listar todas las publicaciones disponibles para suscriptores.

    Atributos:
        model (Post): El modelo que se utilizará para obtener los datos.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        ordering (list): Lista que define el orden de los resultados.
    """
    model = Post
    template_name = 'suscribers/explore.html'
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
        ).order_by('-priority', '-date_posted')
    
    def get_context_data(self, **kwargs):
        """Añade información adicional al contexto, como la lista de categorías."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(
             num_posts=Count('post', filter=Q(post__status='published'))
        ).filter(num_posts__gt=0)
        # Generar una altura aleatoria para cada post en la lista de objetos (object_list)
        [setattr(post, 'height', random.randint(250, 450)) for post in context['object_list']]
        return context

class SuscriberFeedPostsView(ListView):
    """
    Vista para listar todas las publicaciones disponibles para suscriptores.

    Atributos:
        model (Post): El modelo que se utilizará para obtener los datos.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        ordering (list): Lista que define el orden de los resultados.
    """
    model = Post
    template_name = 'suscribers/feed.html'
    ordering = ['-date_posted']
    
    def get_queryset(self):
        # Obtener la hora actual en UTC
        now = timezone.now()
        
        # Condición 1: Si publish_start_date y publish_end_date no son nulos y la fecha actual está en el rango
        programmed = Q(publish_start_date__lte=now, publish_end_date__gte=now, publish_start_date__isnull=False, publish_end_date__isnull=False)

        # Condición 2: Si publish_start_date y publish_end_date son nulos
        regular = Q(publish_start_date__isnull=True, publish_end_date__isnull=True)

        # Obtener el usuario autenticado
        user = self.request.user

        # Obtener las categorías compradas por el usuario
        purchased_categories = user.purchased_categories.all()

        suscribed_categories = user.suscribed_categories.all()

        # Filtrar los posts con status 'published' que cumplan cualquiera de las dos condiciones
        return Post.objects.filter(
            Q(status='published') & (programmed | regular) & (Q(category__in=purchased_categories) | Q(category__in=suscribed_categories))
        ).order_by('-priority', '-date_posted')
    
    def get_context_data(self, **kwargs):
        """Añade información adicional al contexto, como la lista de categorías."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        # Generar una altura aleatoria para cada post en la lista de objetos (object_list)
        [setattr(post, 'height', random.randint(250, 450)) for post in context['object_list']]
        return context

class SearchExplorePostView(ListView):
    """
    Vista para buscar publicaciones basadas en palabras clave, autor, título o categoría,
    respetando las condiciones de publicaciones programadas o regulares.

    Atributos:
        model (Post): El modelo que se utilizará para realizar la búsqueda.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        context_object_name (str): El nombre del contexto que contiene los resultados de la búsqueda.
    """
    model = Post
    template_name = 'suscribers/explore.html'
    context_object_name = 'post_search'

    def get_queryset(self):
        """
        Filtra las publicaciones basadas en la consulta de búsqueda proporcionada,
        respetando las condiciones de fechas y status de las publicaciones.
        
        Returns:
            QuerySet: El conjunto de resultados de la búsqueda.
        """
        # Obtener la hora actual en UTC
        now = timezone.now()

        # Condición 1: Si publish_start_date y publish_end_date no son nulos y la fecha actual está en el rango
        programmed = Q(publish_start_date__lte=now, publish_end_date__gte=now, publish_start_date__isnull=False, publish_end_date__isnull=False)

        # Condición 2: Si publish_start_date y publish_end_date son nulos
        regular = Q(publish_start_date__isnull=True, publish_end_date__isnull=True)

        # Filtro base: status 'published' y las condiciones de fechas programadas o regulares
        base_filter = Post.objects.filter(
            Q(status='published') & (programmed | regular)
        ).order_by('-priority', '-date_posted')

        # Obtener el término de búsqueda
        query = self.request.GET.get('q')

        # Si hay un término de búsqueda, aplicarlo sobre el filtro base
        if query:
            posts = base_filter.filter(
                Q(title__iregex=query) |
                Q(author__first_name__iregex=query) |
                Q(author__last_name__iregex=query) |
                Q(category__name__iregex=query) |
                Q(keywords__iregex=query)
            )
        else:
            posts = base_filter

        return posts

    def get_context_data(self, **kwargs):
        """
        Añade información adicional al contexto, como la lista de categorías.

        Returns:
            dict: El contexto actualizado con la lista de categorías.
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Agregar todas las categorías
        return context

class SearchFeedPostView(ListView):
    """
    Vista para buscar publicaciones basadas en palabras clave, autor, título o categoría,
    respetando las condiciones de publicaciones programadas o regulares y las categorías compradas por el usuario.

    Atributos:
        model (Post): El modelo que se utilizará para realizar la búsqueda.
        template_name (str): La plantilla que se utilizará para renderizar la vista.
        context_object_name (str): El nombre del contexto que contiene los resultados de la búsqueda.
    """
    model = Post
    template_name = 'suscribers/feed.html'  # Plantilla para el feed
    context_object_name = 'post_search'

    def get_queryset(self):
        """
        Filtra las publicaciones basadas en la consulta de búsqueda proporcionada,
        respetando las condiciones de fechas, status de las publicaciones y las categorías compradas por el usuario.
        
        Returns:
            QuerySet: El conjunto de resultados de la búsqueda.
        """
        # Obtener la hora actual en UTC
        now = timezone.now()

        # Condición 1: Si publish_start_date y publish_end_date no son nulos y la fecha actual está en el rango
        programmed = Q(publish_start_date__lte=now, publish_end_date__gte=now, publish_start_date__isnull=False, publish_end_date__isnull=False)

        # Condición 2: Si publish_start_date y publish_end_date son nulos
        regular = Q(publish_start_date__isnull=True, publish_end_date__isnull=True)

        # Obtener el usuario autenticado
        user = self.request.user

        # Obtener las categorías compradas por el usuario
        purchased_categories = user.purchased_categories.all()

        # Filtro base: status 'published', condiciones de fechas, y categorías compradas
        base_filter = Post.objects.filter(
            Q(status='published') & (programmed | regular) & Q(category__in=purchased_categories)
        ).order_by('-priority', '-date_posted')

        # Obtener el término de búsqueda
        query = self.request.GET.get('q')

        # Si hay un término de búsqueda, aplicarlo sobre el filtro base
        if query:
            posts = base_filter.filter(
                Q(title__iregex=query) |
                Q(author__first_name__iregex=query) |
                Q(author__last_name__iregex=query) |
                Q(category__name__iregex=query) |
                Q(keywords__iregex=query)
            )
        else:
            posts = base_filter

        return posts

    def get_context_data(self, **kwargs):
        """
        Añade información adicional al contexto, como la lista de categorías.

        Returns:
            dict: El contexto actualizado con la lista de categorías.
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Agregar todas las categorías
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
        
    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        context['LYKET_API_KEY'] = settings.LYKET_API_KEY
        context['COMMENTBOX_API_KEY'] = settings.COMMENTBOX_API_KEY
        context['DEBUG'] = settings.DEBUG	
        post = self.get_object()
        
        user_email = self.request.user.email if self.request.user.is_authenticated else None
        report_exists = Report.objects.filter(post=post, email=user_email).exists() if user_email else False

        context['report_exists'] = report_exists
        return context
    


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

        moderated_categories = Category.objects.filter(moderated=True)

        if can_create and not can_edit and not can_publish:
            # User can only create posts, show only their posts
            draft_posts = Post.objects.filter(status='draft', author=user, category__in=moderated_categories)
            to_edit_posts = Post.objects.filter(status='to_edit', author=user, category__in=moderated_categories)
            to_publish_posts = Post.objects.filter(status='to_publish', author=user, category__in=moderated_categories)
            published_posts = Post.objects.filter(status='published', author=user, category__in=moderated_categories)
        else:
            # User has other permissions, show all posts
            draft_posts = Post.objects.filter(status='draft', category__in=moderated_categories)
            to_edit_posts = Post.objects.filter(status='to_edit', category__in=moderated_categories)
            to_publish_posts = Post.objects.filter(status='to_publish', category__in=moderated_categories)
            published_posts = Post.objects.filter(status='published', category__in=moderated_categories)

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
                    post.change_reason = "Actualizado desde el tablero Kanban"
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
        context['thumbnail_url'] = default_storage.url(context['post'].thumbnail) if context['post'].thumbnail else None
        return context
    
# views for relevant posts
class RelevantPostsView(ListView):
    model = Post
    template_name = 'relevant/relevant_posts.html'
    ordering = ['-date_posted']

    def get_queryset(self):
        now = timezone.now()

        # Condiciones para posts programados o regulares
        programmed = Q(publish_start_date__lte=now, publish_end_date__gte=now, publish_start_date__isnull=False, publish_end_date__isnull=False)
        regular = Q(publish_start_date__isnull=True, publish_end_date__isnull=True)

        # Filtrar por status publicado y condiciones de fechas
        return Post.objects.filter(
            Q(status='published') & (programmed | regular)
        ).order_by('-priority', '-date_posted')

    def post(self, request, *args, **kwargs):
        """Maneja las acciones para hacer relevante o quitar relevancia a una publicación."""
        post_id = request.POST.get('post_id')
        action = request.POST.get('action')

        # Verificamos si el post_id y la acción están presentes
        if not post_id or not action:
            messages.error(request, "No se pudo realizar la operación.")
            return redirect('relevant_posts')

        # Obtener el post por su ID
        post = get_object_or_404(Post, id=post_id)

        # Si la acción es hacer relevante
        if action == 'make_relevant':
            post.priority = 4  # Hacer relevante, asignamos prioridad 4
            post.save()  # Guardamos el cambio en la base de datos
            messages.success(request, f'El post "{post.title}" ahora es relevante.')

        # Si la acción es quitar relevancia
        elif action == 'remove_relevance':
            post.priority = post.calculate_priority()  # Recalcular la prioridad original
            post.save()  # Guardamos el cambio en la base de datos
            messages.success(request, f'La relevancia del post "{post.title}" ha sido restablecida.')

        # Redirigir a la página relevante para recargar los posts
        return redirect('relevant-posts')
    
class ReportPostView(View):
    """
    Vista para manejar el reporte de un post tanto por usuarios registrados como no registrados.

    Args:
        request (HttpRequest): El objeto de la solicitud.
        post_id (int): El ID del post a reportar.

    Returns:
        HttpResponse: El objeto de respuesta con la plantilla renderizada.
    """
    template_name = 'reports/report_post.html'

    def get(self, request, *args, **kwargs):
        """
        Maneja las solicitudes GET para mostrar el formulario de reporte.

        Args:
            request (HttpRequest): El objeto de la solicitud.
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales.

        Returns:
            HttpResponse: El objeto de respuesta con la plantilla renderizada.
        """
        post = get_object_or_404(Post, id=kwargs.get('pk'))
        form = ReportForm()
        member = None
        if request.user.is_authenticated:
            member = get_object_or_404(Member, username=request.user)
        return render(request, self.template_name, {'form': form, 'post': post, 'member': member})

    def post(self, request, **kwargs):
        """
        Maneja las solicitudes POST para enviar el formulario de reporte.

        Args:
            request (HttpRequest): El objeto de la solicitud.
            **kwargs: Argumentos clave adicionales.

        Returns:
            HttpResponse: Redirige a la URL del post reportado.
        """
        post_id = kwargs.get('pk')
        post = get_object_or_404(Post, id=post_id)
        
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            if request.user.is_authenticated:
                report.member = get_object_or_404(Member, username=request.user)
                report.email = request.user.email
            else:
                report.email = form.cleaned_data.get('email')
            
            try:
                report.save()
                messages.success(request, 'Tu reporte ha sido enviado.')
            except IntegrityError:
                messages.error(request, 'Ya existe un reporte con tu correo.')
        else:
            # Imprimir errores del formulario para depuración
            print(form.errors)
            if 'email' in form.errors:
                messages.error(request, form.errors['email'][0])
            else:
                messages.error(request, "Hubo un error con tu envío.")
        
        return redirect(post.get_absolute_url())
    
class ReportedPostsView(View):
    """
    Vista para mostrar los posts reportados con opciones de filtrado por autor, categoría y estado.

    Args:
        request (HttpRequest): El objeto de la solicitud.

    Returns:
        HttpResponse: El objeto de respuesta con la plantilla renderizada.
    """
    template_name = 'reports/incidents.html'

    def get(self, request, *args, **kwargs):
        """
        Maneja las solicitudes GET para mostrar los posts reportados.

        Args:
            request (HttpRequest): El objeto de la solicitud.
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales.

        Returns:
            HttpResponse: El objeto de respuesta con la plantilla renderizada.
        """
        can_delete_post = request.user.has_perm('posts.delete_post')
        reported_posts = Post.objects.annotate(report_count=Count('reports')).filter(report_count__gt=0).order_by('-report_count')
        if not request.user.has_perm('posts.change_post') and not request.user.has_perm('posts.can_publish'):
            reported_posts = reported_posts.filter(author=request.user)

        return render(request, self.template_name, {
            'reported_posts': reported_posts,
            'can_delete_post':can_delete_post
        })
    
class TogglePostStatusView(LoginRequiredMixin, View):
    """
    Vista para alternar el estado de un post entre 'publicado' e 'inactivo'.

    Args:
        request (HttpRequest): El objeto de la solicitud.
        pk (int): El ID del post a alternar.

    Returns:
        HttpResponse: Redirige a la URL de los posts reportados con los parámetros de filtro preservados.
    """
    def post(self, request, pk, *args, **kwargs):
        """
        Maneja las solicitudes POST para alternar el estado de un post.

        Args:
            request (HttpRequest): El objeto de la solicitud.
            pk (int): El ID del post a alternar.
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales.

        Returns:
            HttpResponse: Redirige a la URL de los posts reportados con los parámetros de filtro preservados.
        """
        post = get_object_or_404(Post, pk=pk)
        if post.status == 'inactive':
            post.status = 'published'
            messages.success(request, 'El post ha sido activado.')
        else:
            post.status = 'inactive'
            messages.success(request, 'El post ha sido inactivado.')
        post.save()

        return redirect(f'{reverse("incidents")}')
    
class SubscribeView(LoginRequiredMixin, View):
    def post(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        if category.kind != 'premium':
            request.user.suscribed_categories.add(category)
            messages.success(request, 'Te haz suscrito a la categoria correctamente.')
        return redirect('category', pk=category.pk, name=category.name)

class UnsubscribeView(LoginRequiredMixin, View):
    def post(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        if category in request.user.suscribed_categories.all():
            request.user.suscribed_categories.remove(category)
            messages.success(request, 'Te haz desuscrito a la categoria correctamente.')
        return redirect('category', pk=category.pk, name=category.name)

class MyCategoriesView(LoginRequiredMixin, ListView):
    template_name = 'suscribers/my_categories.html'
    context_object_name = 'suscribed_categories'

    def get_queryset(self):
        user = self.request.user
        return user.suscribed_categories.all() | user.purchased_categories.all()