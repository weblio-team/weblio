from pyexpat.errors import messages
from django.views.generic import FormView, TemplateView,  CreateView, UpdateView
from django.urls import reverse_lazy, reverse

from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, PasswordChangeView
from .models import Member, Notification
from django import views
from django.views.generic import CreateView, DeleteView
from django.shortcuts import render, get_object_or_404, redirect

from .forms import CreateGroupForm, MemberEditGroupForm, MemberEditPermissionForm, MemberStatusForm, GroupEditForm
from posts.models import Category
from .forms import MemberRegisterForm, MemberJoinForm, MemberLoginForm
from .forms import PasswordChangingForm
from .forms import EditProfileForm, UserAddRoleForm
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch
from django.contrib.auth.models import Permission
from django.utils.translation import gettext as _
from django.conf import settings
from services.views import SendLoginEmailView, AccountStatusEmailView, UserPermissionsEmailView
from dicts import translated_module_dict, translated_submodule_dict, translated_permission_dict
from django.urls import resolve

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': reverse('profile')})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'members/edit_profile.html', {'form': form})

@login_required
def update_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile-pic'):
        request.user.pfp = request.FILES['profile-pic']
        request.user.save()
        return JsonResponse({'success': True, 'redirect_url': reverse('profile')})
    return JsonResponse({'success': False})


class HomeView(TemplateView):
    """
    Vista de la página de inicio.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.
    """
    template_name = 'home.html'

    def dispatch(self, request, *args, **kwargs):
        if settings.DEBUG:
            # URLs para desarrollo con mensajes personalizados
            development_urls = {
                 # URLs for stripe (development)
                'stripe_checkout': "La funcionalidad de Stripe solo está disponible en producción.",
                'payment_success': "La confirmación de pago solo está disponible en producción.",
                'payment_cancel': "La cancelación de pago solo está disponible en producción.",
                 
                # URLs for dashboard (development)
                'posts_claps': "Las vistas de publicaciones solo están disponibles en producción.",
                'posts_updowns': "Los likes de publicaciones solo están disponibles en producción.",
                'posts_rates': "Las estrellas de publicaciones solo están disponibles en producción.",
                'categories_claps': "Las vistas de categorías solo están disponibles en producción.",
                'categories_updowns': "Los likes de categorías solo están disponibles en producción.",
                'categories_rates': "Las estrellas de categorías solo están disponibles en producción.",
                'posts_dashboard': "El dashboard solo está disponible en producción.",
                
                # URLs for password reset email (development)
                'reset_password_email': "El reseteo de contraseña por correo solo está disponible en producción.",
                'password_reset_done_email': "La confirmación de reseteo de contraseña por correo solo está disponible en producción.",
                'password_reset_confirm_email': "La confirmación de reseteo de contraseña por correo solo está disponible en producción.",
                'password_reset_complete_email': "La finalización de reseteo de contraseña por correo solo está disponible en producción."
            }

            # Obtener el nombre de la URL actual
            current_url_name = resolve(request.path_info).url_name

            # Verificar si la URL actual está en el diccionario de URLs de desarrollo
            if current_url_name in development_urls:
                messages.warning(request, development_urls[current_url_name])
                return redirect('home')  # Redirigir a una página adecuada, por ejemplo, la página de inicio

        return super().dispatch(request, *args, **kwargs)

# views for groups
class GroupListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Vista para listar todos los grupos junto con sus permisos.
    """

    template_name = 'groups/group_list.html'
    permission_required = ['auth.view_group',]

    def get_context_data(self, **kwargs):
        """
        Agrega los grupos con sus permisos traducidos al contexto de la plantilla.
        """
        context = super().get_context_data(**kwargs)
        groups = Group.objects.all().prefetch_related('permissions')

        # Traducir y agrupar permisos para cada grupo
        translated_groups = []
        for group in groups:
            grouped_permissions = self.get_grouped_permissions(group)
            translated_groups.append({
                'group': group,
                'grouped_permissions': grouped_permissions
            })

        context['translated_groups'] = translated_groups
        return context

    def get_grouped_permissions(self, group):
        """
        Agrupa y traduce los permisos de un grupo para mostrarlos en el listado.
        """
        permissions = group.permissions.exclude(content_type__model__in=['historicalpost',
                                                                         'session',
                                                                         'contenttype'
                                                                         'logentry',
                                                                         ]
        ).select_related('content_type')
        grouped_permissions = {}
        for perm in permissions:
            module_name = perm.content_type.app_label.capitalize()
            submodule_name = perm.content_type.model.capitalize()

            # Traducción de módulos y submódulos
            translated_module = translated_module_dict.get(perm.content_type.app_label, module_name)

            # Traducción de submódulos
            translated_submodule = translated_submodule_dict.get(perm.content_type.model, submodule_name)

            # Traducción de permisos
            translated_permission = translated_permission_dict.get(perm.name, perm.name)

            # Agrupar los permisos traducidos por módulo y submódulo
            if translated_module not in grouped_permissions:
                grouped_permissions[translated_module] = {}
            if translated_submodule not in grouped_permissions[translated_module]:
                grouped_permissions[translated_module][translated_submodule] = []

            grouped_permissions[translated_module][translated_submodule].append(translated_permission)

        return grouped_permissions
    
    def post(self, request, *args, **kwargs):
        selected_group_id = request.POST.get('selected_group')
        action = request.POST.get('action')
        if selected_group_id:
            if action == 'edit_group':
                return redirect('group-edit', pk=selected_group_id)
            if action == 'delete_group':
                return redirect('group-delete', group_id=selected_group_id)
        return self.get(request, *args, **kwargs)

class GroupEditView(FormView):
    """
    Vista para editar un grupo.

    Métodos:
        - get: Recupera el grupo especificado por pk y muestra un formulario para editar sus permisos.
        - post: Procesa el formulario enviado para actualizar los permisos del grupo.
    """
    
    template_name = 'groups/group_edit.html'
    form_class = GroupEditForm

    def get_context_data(self, **kwargs):
        """
        Agrega los permisos agrupados y traducidos al contexto del formulario.

        Args:
            kwargs: Argumentos adicionales pasados al contexto.

        Returns:
            dict: Contexto con el formulario y los permisos agrupados y traducidos.
        """
        context = super().get_context_data(**kwargs)
        group = self.get_group()

        # Obtener el formulario con los permisos actuales del grupo
        form = self.get_form()

        # Obtener permisos agrupados y traducidos
        grouped_permissions = self.get_grouped_permissions(group)

        # Lista de IDs de los permisos actuales del grupo
        selected_permissions_ids = group.permissions.values_list('id', flat=True)

        # Añadir los permisos agrupados y traducidos al contexto
        context.update({
            'form': form,
            'group': group,
            'grouped_permissions': grouped_permissions,
            'selected_permissions_ids': list(selected_permissions_ids)  # Pasar como lista
        })
        return context

    def get_group(self):
        """
        Recupera el grupo especificado por pk.

        Returns:
            Group: El grupo a editar.
        """
        pk = self.kwargs.get('pk')
        return get_object_or_404(Group, pk=pk)

    def get_grouped_permissions(self, group):
        """
        Agrupa y traduce los permisos para mostrarlos en el formulario.

        Args:
            group: El grupo cuyos permisos se agruparán.

        Returns:
            dict: Permisos agrupados por módulo y submódulo.
        """
        # Excluir permisos no deseados
        permissions = Permission.objects.exclude(
            content_type__model__in=['historicalpost', 'contenttype', 'session', 'logentry', 'site']
        ).select_related('content_type').distinct()

        grouped_permissions = {}
        for perm in permissions:
            module_name = perm.content_type.app_label.capitalize()
            submodule_name = perm.content_type.model.capitalize()

            # Traducción de módulos y submódulos
            translated_module = translated_module_dict.get(perm.content_type.app_label, module_name)

            # Traducción de submódulos
            translated_submodule = translated_submodule_dict.get(perm.content_type.model, submodule_name)

            # Traducción de permisos
            translated_permission = translated_permission_dict.get(perm.name, perm.name)

            if translated_module not in grouped_permissions:
                grouped_permissions[translated_module] = {}
            if translated_submodule not in grouped_permissions[translated_module]:
                grouped_permissions[translated_module][translated_submodule] = []

            grouped_permissions[translated_module][translated_submodule].append({
                'id': perm.id,
                'name': translated_permission  # Usar la traducción del permiso
            })

        return grouped_permissions

    def post(self, request, pk):
        """
        Procesa el formulario enviado para actualizar los permisos del grupo.

        Args:
            request: La solicitud HTTP que contiene los datos del formulario.
            pk: El identificador del grupo a actualizar.

        Returns:
            Redirige a la lista de grupos si el formulario es válido, o renderiza el formulario con errores.
        """
        group = get_object_or_404(Group, pk=pk)
        form = GroupEditForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, f'El grupo "{group.name}" ha sido actualizado.')
            return redirect('group-list')
        context = {
            'form': form,
            'group': group,
            'grouped_permissions': self.get_grouped_permissions(group),
            'selected_permissions_ids': list(group.permissions.values_list('id', flat=True))
        }
        return render(request, self.template_name, context)


class GroupDeleteView(DeleteView):
    """
    Vista para eliminar un grupo.

    Métodos:
        - get: Recupera el grupo especificado por group_id y muestra una página de confirmación de eliminación.
        - post: Procesa la solicitud de eliminación del grupo, verificando que no deje a ningún miembro sin grupo.
    """
    
    model = Group
    template_name = 'groups/group_delete.html'
    success_url = reverse_lazy('group-list')

    def get(self, request, group_id, *args, **kwargs):
        """
        Recupera el grupo especificado por group_id y muestra una página de confirmación de eliminación.

        Args:
            request: La solicitud HTTP.
            group_id: El identificador del grupo a eliminar.

        Returns:
            Renderiza la plantilla 'groups/group_delete.html' con el grupo y los miembros asociados.
        """
        group = get_object_or_404(Group, id=group_id)
        members = Member.objects.annotate(group_count=Count('groups'))
        members = members.filter(groups=group).order_by('group_count')
        members_with_single_group = [member for member in members if member.group_count == 1]

        if members_with_single_group:
            return render(request, self.template_name, {
                'group': group, 
                'members': members,
                'members_with_single_group': members_with_single_group,
                'error': 'No se puede eliminar. Existen usuarios que se quedarían sin rol.'
            })
        
        return render(request, self.template_name, {
                'group': group, 
                'members': members
            })

    def post(self, request, group_id, *args, **kwargs):
        """
        Procesa la solicitud de eliminación del grupo.

        Args:
            request: La solicitud HTTP que contiene los datos del formulario.
            group_id: El identificador del grupo a eliminar.

        Returns:
            Redirige a la vista de edición de grupo si se selecciona 'edit_group', o elimina el grupo y redirige a la lista de grupos si se confirma la eliminación.
        """
        action = request.POST.get('action')
        if action == 'edit_group':
            selected_member = request.POST.get('selected_member')
            return redirect(f'{reverse_lazy("member-edit-group", kwargs={"pk": selected_member})}?next={self.request.path}')
        elif action == 'confirm':
            group = get_object_or_404(Group, id=group_id)
            members = Member.objects.annotate(group_count=Count('groups'))
            members = members.filter(groups=group).order_by('group_count')
            members_with_single_group = [member for member in members if member.group_count == 1]

            if members_with_single_group:
                return render(request, self.template_name, {
                    'group': group, 
                    'members': members,
                    'members_with_single_group': members_with_single_group,
                    'error': 'No se puede eliminar. Existen usuarios que se quedarían sin rol.'
                })

            group.delete()
            return redirect(self.success_url)

class CreateGroupView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """
    Vista para crear un nuevo grupo y asignarle permisos.

    Muestra un formulario que permite ingresar un nombre para el nuevo grupo
    y asignarle múltiples permisos.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.
        form_class (class): Clase del formulario que se utiliza en la vista.
        success_url (str): URL a la que se redirige después de que el formulario es válido.
        permission_required (list): Lista de permisos requeridos para acceder a la vista.

    Métodos:
        form_valid(form): Método que se ejecuta cuando el formulario es válido y guarda el nuevo grupo.
    """
    template_name = 'groups/group_create.html'
    form_class = CreateGroupForm
    success_url = reverse_lazy('group-list')
    permission_required = ['auth.add_group', 
                           'auth.add_permission'
        ]

    def get_context_data(self, **kwargs):
        """
        Agrega los permisos agrupados y traducidos al contexto del formulario.

        Returns:
            dict: Contexto con el formulario y los permisos agrupados.
        """
        context = super().get_context_data(**kwargs)
        form = self.get_form()

        # Obtener permisos agrupados y traducidos
        grouped_permissions = self.get_grouped_permissions()

        # Añadir los permisos agrupados al contexto
        context.update({
            'form': form,
            'grouped_permissions': grouped_permissions
        })

        return context

    def get_grouped_permissions(self):
        """
        Agrupa y traduce los permisos para mostrarlos en el formulario.

        Returns:
            dict: Permisos agrupados por módulo y submódulo.
        """
        # Excluye los permisos no deseados y selecciona los que pertenecen al grupo
        permissions = Permission.objects.exclude(
            content_type__model__in=['historicalpost', 'contenttype', 'session', 'logentry', 'site']
        ).select_related('content_type').distinct()

        grouped_permissions = {}
        for perm in permissions:
            module_name = perm.content_type.app_label.capitalize()
            submodule_name = perm.content_type.model.capitalize()

            # Traducción de módulos y submódulos
            translated_module = translated_module_dict.get(perm.content_type.app_label, module_name)

            # Traducción de submódulos
            translated_submodule = translated_submodule_dict.get(perm.content_type.model, submodule_name)

            # Traducción de permisos
            translated_permission = translated_permission_dict.get(perm.name, perm.name)
            # Agrupación de permisos
            if translated_module not in grouped_permissions:
                grouped_permissions[translated_module] = {}
            if translated_submodule not in grouped_permissions[translated_module]:
                grouped_permissions[translated_module][translated_submodule] = []

            grouped_permissions[translated_module][translated_submodule].append({
                'id': perm.id,
                'name': translated_permission  # Usar la traducción del permiso
            })
        
        # Eliminar el permiso 'Puede ver dashboard' si esta en debug
        if settings.DEBUG:
            grouped_permissions = {
                module: {
                    submodule: [perm for perm in perms if perm['name'] != 'Puede ver dashboard']
                    for submodule, perms in submodules.items()
                }
                for module, submodules in grouped_permissions.items()
            }
        return grouped_permissions

    def form_valid(self, form):
        """
        Procesa el formulario cuando es válido.

        Este método guarda el nuevo grupo y asigna los permisos seleccionados.

        Args:
            form (CreateGroupForm): El formulario que ha sido validado.

        Returns:
            HttpResponse: Redirige a `success_url` después de crear el grupo.
        """
        form.save()
        messages.success(self.request, "El grupo ha sido creado.")
        return super().form_valid(form)

# views for members
class MemberListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Vista para listar todos los miembros con su grupo y permisos.
    """

    template_name = 'members/member_list.html'
    permission_required = ['auth.view_member']

    def get_context_data(self, **kwargs):
        """
        Agrega los miembros con sus grupos y permisos al contexto de la plantilla.
        """
        context = super().get_context_data(**kwargs)
        
        # Obtener todos los miembros y prefetch los permisos excluyendo los modelos no deseados
        members = Member.objects.all().prefetch_related(
            Prefetch(
                'user_permissions',
                queryset=Permission.objects.exclude(
                    content_type__model__in=['historicalpost', 'logentry', 'session', 'contenttype']
                ).select_related('content_type')
            )
        ).prefetch_related('groups')

        # Agrupar permisos para cada miembro
        member_list = []
        for member in members:
            grouped_permissions = {}
            for perm in member.user_permissions.all():
                module_name = perm.content_type.app_label.capitalize()
                submodule_name = perm.content_type.model.capitalize()

                # Traducción de módulos y submódulos
                translated_module = translated_module_dict.get(perm.content_type.app_label, module_name)

                # Traducción de submódulos
                translated_submodule = translated_submodule_dict.get(perm.content_type.model, submodule_name)

                # Traducción de permisos
                translated_permission = translated_permission_dict.get(perm.name, perm.name)

                # Agrupar permisos
                if translated_module not in grouped_permissions:
                    grouped_permissions[translated_module] = {}
                if translated_submodule not in grouped_permissions[translated_module]:
                    grouped_permissions[translated_module][translated_submodule] = []
                grouped_permissions[translated_module][translated_submodule].append(translated_permission)

            member_list.append({
                'member': member,
                'grouped_permissions': grouped_permissions,
            })

        context['members'] = member_list
        return context

    def post(self, request, *args, **kwargs):
        """
        Maneja la selección de un miembro y redirige a la página de edición.
        """
        selected_member_id = request.POST.get('selected_member')
        action = request.POST.get('action')

        if selected_member_id:
            if action == 'edit_group':
                return redirect('member-edit-group', pk=selected_member_id)
            elif action == 'edit_permission':
                return redirect('member-edit-permission', pk=selected_member_id)
            elif action == 'toggle_status':
                return redirect('member-status', pk=selected_member_id)

        return self.get(request, *args, **kwargs)


class MemberEditGroupView(LoginRequiredMixin, PermissionRequiredMixin, views.View):
    """
    Vista para editar los grupos de un miembro.
    Atributos:
        permission_required (list): Lista de permisos requeridos para acceder a la vista.
    """

    permission_required = ['auth.change_member']

    def get(self, request, pk):
        """
        Obtiene el formulario de edición de grupos para un miembro existente.
        Parámetros:
        - request: La solicitud HTTP recibida.
        - pk: El ID del miembro a editar.
        Retorna:
        - Una respuesta HTTP con el formulario de edición de grupos y el miembro.
        """
        member = get_object_or_404(Member, pk=pk)
        form = MemberEditGroupForm(instance=member)

        # Get the IDs of the groups already assigned to the member
        selected_group_ids = member.groups.values_list('id', flat=True)

        # Obtener los roles (grupos) y permisos agrupados y traducidos
        translated_groups = self.get_translated_groups()

        next_url = request.GET.get('next', '')
        return render(request, 'members/edit_group.html', {
            'form': form,
            'member': member,
            'translated_groups': translated_groups,
            'selected_group_ids': list(selected_group_ids),  # Pasar los grupos seleccionados
            'next_url': next_url
        })

    def post(self, request, pk):
        """
        Procesa el formulario enviado para actualizar los roles del miembro.
        """
        member = get_object_or_404(Member, pk=pk)
        form = MemberEditGroupForm(request.POST, instance=member)

        if form.is_valid():
            # Obtener los grupos actuales antes de actualizar
            current_groups = set(member.groups.all())
            member = form.save(commit=False)
            new_groups = set(form.cleaned_data['groups'])
            
            # Determinar los grupos desasignados
            removed_groups = current_groups - new_groups
            
            # Actualizar los grupos del miembro
            member.groups.set(new_groups)
            member.save()

            # Desasignar permisos de los grupos removidos
            for group in removed_groups:
                member.user_permissions.remove(*group.permissions.all())

            # Asignar los permisos de los nuevos grupos seleccionados
            for group in new_groups:
                member.user_permissions.add(*group.permissions.all())

            next_url = request.GET.get('next')
            messages.success(self.request, "Los grupos y permisos del miembro han sido actualizados.")
            if next_url:
                return redirect(next_url)
            return redirect('member-list')  # Por defecto, redirigir a la lista de miembros
        
        # Si hay errores, volver a renderizar el formulario
        return render(request, 'members/edit_group.html', {
            'form': form,
            'member': member,
            'selected_group_ids': member.groups.values_list('id', flat=True)  # Mantener los IDs seleccionados en caso de error
        })

    def get_translated_groups(self):
        """
        Agrupa y traduce los permisos de los grupos para mostrarlos en la vista.
        Excluye los grupos como 'Admin', 'Contenttypes', y sus permisos.
        
        Returns:
            list: Lista de grupos traducidos con sus permisos agrupados.
        """
        groups = Group.objects.exclude(name__in=['Admin', 'Contenttypes', 'Sessions']).prefetch_related(
            Prefetch('permissions', queryset=Permission.objects.exclude(content_type__model__in=['historicalpost', 'session', 'contenttype', 'logentry']).select_related('content_type'))
        )

        translated_groups = []
        for group in groups:
            grouped_permissions = self.get_grouped_permissions(group)
            translated_groups.append({
                'group': group,
                'grouped_permissions': grouped_permissions
            })

        return translated_groups

    def get_grouped_permissions(self, group):
        """
        Agrupa y traduce los permisos de un grupo para mostrarlos en la vista.
        """
        permissions = group.permissions.exclude(content_type__model__in=['historicalpost', 'session', 'contenttype', 'logentry']).select_related('content_type')
        
        grouped_permissions = {}
        for perm in permissions:
            module_name = perm.content_type.app_label.capitalize()
            submodule_name = perm.content_type.model.capitalize()

            # Traducción de módulos y submódulos
            translated_module = translated_module_dict.get(perm.content_type.app_label, module_name)

            # Traducción de submódulos
            translated_submodule = translated_submodule_dict.get(perm.content_type.model, submodule_name)

            # Traducción de permisos
            translated_permission = translated_permission_dict.get(perm.name, perm.name)

            # Agrupar los permisos traducidos por módulo y submódulo
            if translated_module not in grouped_permissions:
                grouped_permissions[translated_module] = {}
            if translated_submodule not in grouped_permissions[translated_module]:
                grouped_permissions[translated_module][translated_submodule] = []

            grouped_permissions[translated_module][translated_submodule].append(translated_permission)
        
        if settings.DEBUG:
            grouped_permissions = {
                module: {
                submodule: [perm for perm in perms if perm != 'Puede ver dashboard']
                    for submodule, perms in submodules.items()
                }
                for module, submodules in grouped_permissions.items()
            }
        return grouped_permissions

class MemberEditPermissionView(LoginRequiredMixin, PermissionRequiredMixin, views.View):
    """
    Vista de edición de permisos de miembro.
    Esta vista permite editar los permisos de un miembro específico.
    """

    permission_required = ['auth.change_member']

    def get(self, request, pk):
        """
        Obtiene el formulario de edición de permisos y los permisos actuales del miembro.
        """
        member = get_object_or_404(Member, pk=pk)
        form = MemberEditPermissionForm(instance=member)

        # Obtener los permisos agrupados y traducidos
        translated_permissions = self.get_translated_permissions(member)
        group_names = member.groups.values_list('name', flat=True)

        return render(request, 'members/edit_permission.html', {
            'form': form,
            'member': member,
            'translated_permissions': translated_permissions,
            'group_names': group_names,
            'selected_permissions': member.user_permissions.values_list('id', flat=True)
        })

    def post(self, request, pk):
        """
        Guarda los cambios realizados en el formulario de edición de permisos.
        """
        member = get_object_or_404(Member, pk=pk)
        form = MemberEditPermissionForm(request.POST, instance=member)
        if form.is_valid():
            member = form.save(commit=False)
            member.save()

            # Obtener la instancia de Notification del usuario
            try:
                notification = Notification.objects.get(user=member)
            except Notification.DoesNotExist:
                notification = None

            # Verificar si la notificación de "Informar sobre actualización de permisos" está activada
            if notification and 'Informar sobre actualización de permisos' in notification.additional_notifications and not settings.DEBUG:
                # Enviar correo de notificación al usuario
                email_view = UserPermissionsEmailView()
                email_view.send_permissions_email(member, member.email)

            # Asignar los permisos seleccionados
            member.user_permissions.set(form.cleaned_data['permissions'])
            messages.success(self.request, "Los permisos del miembro han sido actualizados.")
            return redirect('member-list')

        # En caso de errores, renderizamos la vista con los permisos actuales
        translated_permissions = self.get_translated_permissions(member)
        return render(request, 'members/edit_permission.html', {
            'form': form,
            'member': member,
            'translated_permissions': translated_permissions,
            'selected_permissions': member.user_permissions.values_list('id', flat=True)
        })

    def get_translated_permissions(self, member):
        """
        Agrupa y traduce los permisos de los grupos para mostrarlos en la vista.
        """
        permissions = Permission.objects.filter(group__in=member.groups.all()).distinct()

        grouped_permissions = {}
        for perm in permissions:
            module_name = perm.content_type.app_label.capitalize()
            submodule_name = perm.content_type.model.capitalize()

            # Traducción de módulos y submódulos
            translated_module = translated_module_dict.get(perm.content_type.app_label, module_name)

            # Traducción de submódulos
            translated_submodule = translated_submodule_dict.get(perm.content_type.model, submodule_name)

            # Traducción de permisos
            translated_permission = translated_permission_dict.get(perm.name, perm.name)

            # Agrupación de permisos
            if translated_module not in grouped_permissions:
                grouped_permissions[translated_module] = {}
            if translated_submodule not in grouped_permissions[translated_module]:
                grouped_permissions[translated_module][translated_submodule] = []

            grouped_permissions[translated_module][translated_submodule].append({
                'id': perm.id,
                'name': translated_permission
            })

        return grouped_permissions

class MemberStatusView(LoginRequiredMixin, PermissionRequiredMixin, views.View):
    """
    Vista para mostrar y actualizar el estado de un miembro.
    Attributes:
        template_name (str): El nombre de la plantilla HTML para renderizar la vista.
        permission_required (list): Lista de permisos requeridos para acceder a la vista.
    """
    template_name = 'members/member_status.html'
    permission_required = ['auth.change_member',
        ]

    def get(self, request, pk):
        """
        Obtiene un miembro específico y muestra el formulario para actualizar su estado.
            Args:
                request (HttpRequest): La solicitud HTTP recibida.
                pk (int): El ID del miembro.
            Returns:
                HttpResponse: La respuesta HTTP que muestra el formulario de estado del miembro.
        """

        member = get_object_or_404(Member, pk=pk)
        form = MemberStatusForm(instance=member)
        return render(request, self.template_name, {'form': form, 'member': member})

    def post(self, request, pk):
        """
         Actualiza el estado de un miembro específico según los datos enviados en la solicitud POST.
            Args:
                request (HttpRequest): La solicitud HTTP recibida.
                pk (int): El ID del miembro.
            Returns:
                HttpResponse: La respuesta HTTP que redirige a la lista de miembros si el formulario es válido,
                o muestra el formulario de estado del miembro con errores si el formulario no es válido.
        """
        member = get_object_or_404(Member, pk=pk)
        form = MemberStatusForm(request.POST, instance=member)
        if form.is_valid():
            """
            Método que se llama tras el POST del form con datos válidos.
            """
            member = form.save()
            account_status = 'activada' if member.is_active else 'desactivada'

            # Obtener la instancia de Notification del usuario
            try:
                notification = Notification.objects.get(user=member)
            except Notification.DoesNotExist:
                notification = None

            # Verificar si la notificación de "Informar sobre activación/inactivación de cuenta" está activada
            if notification and 'Informar sobre activación/inactivación de cuenta' in notification.additional_notifications and not settings.DEBUG:
                # Enviar correo de notificación al usuario
                email_view = AccountStatusEmailView()
                email_view.send_account_status_email(member, account_status, member.email)

            messages.success(self.request, f"La cuenta del miembro ha sido {account_status}.")
            return redirect('member-list')
        return render(request, self.template_name, {'form': form, 'member': member})
    

class MemberRegisterView(CreateView):
    """
    Vista para registrar nuevos miembros.

    Esta vista permite registrar nuevos miembros utilizando el formulario `MemberRegisterForm`.
    Si el formulario es válido, redirige al usuario a la página de inicio de sesión.
    Si el formulario es inválido, muestra mensajes de advertencia específicos para los errores
    de nombre de usuario y correo electrónico.

    Atributos:
    ----------
    form_class : class
        La clase del formulario que se utilizará para registrar nuevos miembros.
    template_name : str
        El nombre de la plantilla que se utilizará para renderizar la vista.
    success_url : str
        La URL a la que se redirigirá al usuario si el formulario es válido.

    Métodos:
    --------
    form_invalid(form):
        Maneja el caso en que el formulario es inválido, mostrando mensajes de advertencia
        específicos para los errores de nombre de usuario y correo electrónico.
    """
    form_class = MemberRegisterForm
    template_name = 'members/member_register.html'
    success_url = reverse_lazy('member-login')

    def form_invalid(self, form):
        """
        Maneja el caso en que el formulario es inválido.

        Si el formulario contiene errores de nombre de usuario o correo electrónico,
        muestra mensajes de advertencia específicos. También muestra los errores de Django.

        Parameters:
        -----------
        form : Form
            El formulario que contiene los datos inválidos.

        Returns:
        --------
        HttpResponse
            La respuesta HTTP con el formulario inválido renderizado.
        """
        # Validar si el usuario ya está registrado
        if 'username' in form.errors:
            messages.warning(self.request, "El nombre de usuario ya está registrado.")
        # Validar si el correo electrónico ya está registrado
        if 'email' in form.errors:
            messages.warning(self.request, "El correo electrónico ya está registrado.")
        # Mostrar los errores de Django
        for field, errors in form.errors.items():
            for error in errors:
                if 'username' in error and 'email' not in error:
                    messages.warning(self.request, f"{field}: {error}")
        return super().form_invalid(form)

    def form_valid(self, form):
        """
        Maneja el caso en que el formulario es válido.

        Muestra un mensaje de éxito y redirige al usuario a la página de inicio de sesión.

        Parameters:
        -----------
        form : Form
            El formulario que contiene los datos válidos.

        Returns:
        --------
        HttpResponse
            La respuesta HTTP con el formulario válido renderizado.
        """
        response = super().form_valid(form)
        messages.success(self.request, "La cuenta ha sido creada. Por favor, inicie sesión.")
        return response


class MemberLoginView(LoginView):
    """
    Vista para el inicio de sesión de miembros.

    Esta vista permite a los miembros iniciar sesión utilizando el formulario `MemberLoginForm`.
    Si el formulario es válido, muestra un mensaje de bienvenida y redirige al usuario a la URL de éxito.
    Si el formulario es inválido, muestra mensajes de advertencia específicos para los errores de inicio de sesión.

    Atributos:
    ----------
    form_class : class
        La clase del formulario que se utilizará para el inicio de sesión.
    template_name : str
        El nombre de la plantilla que se utilizará para renderizar la vista.

    Métodos:
    --------
    form_valid(form):
        Maneja el caso en que el formulario es válido, mostrando un mensaje de bienvenida
        y redirigiendo al usuario a la URL de éxito.
    form_invalid(form):
        Maneja el caso en que el formulario es inválido, mostrando mensajes de advertencia
        específicos para los errores de inicio de sesión.
    get_success_url():
        Devuelve la URL a la que se redirigirá al usuario si el formulario es válido.
    """
    form_class = MemberLoginForm
    template_name = 'members/member_login.html'

    def form_valid(self, form):
        """
        Maneja el caso en que el formulario es válido.

        Muestra un mensaje de bienvenida y redirige al usuario a la URL de éxito.

        Parameters:
        -----------
        form : Form
            El formulario que contiene los datos válidos.

        Returns:
        --------
        HttpResponse
            La respuesta HTTP con el formulario válido renderizado.
        """
        response = super().form_valid(form)

        # Obtener la instancia de Notification del usuario
        try:
            notification = Notification.objects.get(user=self.request.user)
        except Notification.DoesNotExist:
            notification = None

        # Verificar si la notificación de "Informar sobre inicio de sesión" está activada
        if notification and 'Informar sobre inicio de sesión' in notification.additional_notifications and not settings.DEBUG:
            # Enviar correo de notificación al usuario
            email_view = SendLoginEmailView()
            email_view.send_email(self.request.user, self.request)

        messages.success(self.request, "Bienvenido de vuelta " + self.request.user.username)
        return response

    def form_invalid(self, form):
        """
        Maneja el caso en que el formulario es inválido.

        Si el formulario contiene errores de nombre de usuario o contraseña, muestra mensajes de advertencia específicos.
        También verifica si la cuenta del usuario está inactiva.

        Parameters:
        -----------
        form : Form
            El formulario que contiene los datos inválidos.

        Returns:
        --------
        HttpResponse
            La respuesta HTTP con el formulario inválido renderizado.
        """
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        self.user = authenticate(self.request, username=username, password=password)
        if self.user is not None:
            if not self.user.is_active:
                messages.warning(self.request, "Su cuenta está inactiva. Por favor, contacte al administrador para más detalles.")
                return HttpResponseRedirect(reverse_lazy('login')) 
        else:
            messages.warning(self.request, "Error en el nombre de usuario o contraseña. Por favor, intente de nuevo.")
        return super().form_invalid(form)
    
    def get_success_url(self):
        """
        Devuelve la URL a la que se redirigirá al usuario si el formulario es válido.

        Returns:
        --------
        str
            La URL de éxito.
        """
        return reverse_lazy('posts')
    

class MemberJoinView(CreateView):
    """
    Vista para que los miembros se unan.

    Esta vista permite a los nuevos miembros registrarse utilizando el formulario `MemberJoinForm`.
    Si el formulario es válido, redirige al usuario a la página de inicio y muestra un mensaje de éxito.
    Si el formulario es inválido, muestra los errores correspondientes.

    Atributos:
    ----------
    form_class : class
        La clase del formulario que se utilizará para registrar nuevos miembros.
    template_name : str
        El nombre de la plantilla que se utilizará para renderizar la vista.
    success_url : str
        La URL a la que se redirigirá al usuario si el formulario es válido.

    Métodos:
    --------
    get_context_data(**kwargs):
        Añade los roles disponibles al contexto de la plantilla.
    form_valid(form):
        Maneja el caso en que el formulario es válido, mostrando un mensaje de éxito
        y redirigiendo al usuario a la página de inicio.
    """
    form_class = MemberJoinForm
    template_name = 'members/member_join.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        """
        Añade los roles disponibles al contexto de la plantilla.

        Parameters:
        -----------
        **kwargs : dict
            Argumentos adicionales de palabras clave.

        Returns:
        --------
        dict
            El contexto actualizado con los roles disponibles.
        """
        context = super().get_context_data(**kwargs)
        roles = Group.objects.exclude(name='suscriptor')
        context['roles'] = roles
        return context

    def form_valid(self, form):
        """
        Maneja el caso en que el formulario es válido.

        Muestra un mensaje de éxito y redirige al usuario a la página de inicio.

        Parameters:
        -----------
        form : Form
            El formulario que contiene los datos válidos.

        Returns:
        --------
        HttpResponse
            La respuesta HTTP con el formulario válido renderizado.
        """
        response = super().form_valid(form)
        messages.success(self.request, "La cuenta ha sido creada pero no será activada hasta que un administrador apruebe el login.")
        return response

# views for error pages
class Error404View(TemplateView):
    """
    Vista para mostrar la página de error 404.
    Atributos:
    - template_name (str): El nombre de la plantilla HTML para mostrar la página de error.
    """
    template_name = 'error.html'

    def get_context_data(self, **kwargs):
        """
        Obtiene los datos del contexto para la página de error.
        Parámetros:
        - kwargs (dict): Argumentos clave-valor adicionales para el contexto.
        Retorna:
        - dict: El contexto con los datos de error.
        """
        context = super().get_context_data(**kwargs)
        context['error_code'] = 404
        context['error_message'] = 'Página no encontrada'
        context['error_description'] = 'La página que estás buscando no existe o fue movida.'
        return context


class Error500View(TemplateView):
    """
    Vista para manejar errores internos del servidor.
    Atributos:
    - template_name (str): El nombre de la plantilla a utilizar para mostrar el error.
    Métodos:
    - get_context_data(**kwargs): Retorna un diccionario con los datos del contexto para la plantilla.
    """
    template_name = 'error.html'

    def get_context_data(self, **kwargs):
        """
        Retorna un diccionario con los datos del contexto para la plantilla.
        Parámetros:
        - kwargs (dict): Argumentos clave adicionales.
        Retorna:
        - context (dict): Un diccionario con los datos del contexto.
        """
        context = super().get_context_data(**kwargs)
        context['error_code'] = 500
        context['error_message'] = 'Error interno del servidor'
        context['error_description'] = 'Ocurrió un problema con el servidor. Estamos trabajando para resolverlo.'
        return context
    
class Error403View(TemplateView):
    """
    Vista para manejar errores internos del servidor.
    Atributos:
    - template_name (str): El nombre de la plantilla a utilizar para mostrar el error.
    Métodos:
    - get_context_data(**kwargs): Retorna un diccionario con los datos del contexto para la plantilla.
    """
    template_name = 'error.html'

    def get_context_data(self, **kwargs):
        """
        Retorna un diccionario con los datos del contexto para la plantilla.
        Parámetros:
        - kwargs (dict): Argumentos clave adicionales.
        Retorna:
        - context (dict): Un diccionario con los datos del contexto.
        """
        context = super().get_context_data(**kwargs)
        context['error_code'] = 403
        context['error_message'] = 'No tienes permiso para acceder a esta página'
        context['error_description'] = 'No tienes permiso para acceder a esta página. Por favor, contacta al administrador.'
        return context
    
class UserEditView(UpdateView):
    """
    Vista para editar el perfil del usuario.

    Atributos:
        form_class (EditProfileForm): El formulario utilizado para editar el perfil.
        template_name (str): La plantilla utilizada para renderizar la vista.
        success_url (str): La URL a la que redirigir después de una edición exitosa.
    """
    form_class = EditProfileForm
    template_name = 'members/edit_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        """
        Obtener el objeto del usuario actual.

        Returns:
            User: El usuario actual.
        """
        return self.request.user

    def form_valid(self, form):
        """
        Guardar la foto de perfil si se ha subido una y el formulario es válido.

        Args:
            form (EditProfileForm): El formulario de edición de perfil.

        Returns:
            HttpResponse: La respuesta HTTP después de procesar el formulario.
        """
        response = super().form_valid(form)
        if 'profile-pic-upload' in self.request.FILES:
            self.request.user.pfp = self.request.FILES['profile-pic-upload']
            self.request.user.save()
        return response

    def post(self, request, *args, **kwargs):
        """
        Manejar la solicitud POST para eliminar la foto de perfil.

        Args:
            request (HttpRequest): La solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales.

        Returns:
            HttpResponse: La respuesta HTTP después de procesar la solicitud.
        """
        if 'delete-photo' in request.POST:
            user = self.get_object()
            user.pfp.delete()
            user.save()
            return redirect('profile')
        return super().post(request, *args, **kwargs)
        
class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Vista basada en clases para mostrar el perfil del usuario.

    Atributos:
        template_name: La plantilla que se utilizará para renderizar la vista.

    Métodos:
        get_context_data: Agrega datos adicionales al contexto de la plantilla.
    """
    template_name = 'members/profile.html'
    
    def get_context_data(self, **kwargs):
        """
        Agrega datos adicionales al contexto de la plantilla.

        Args:
            **kwargs: Argumentos adicionales que se pasan al método.

        Returns:
            dict: El contexto actualizado con los datos adicionales.
        """
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
class PasswordsChangeView(PasswordChangeView):
    """
    Vista basada en clases para el cambio de contraseña del usuario.

    Atributos:
        form_class: El formulario que se utilizará para cambiar la contraseña del usuario.
        success_url: La URL a la que se redirigirá después de que la contraseña se haya cambiado con éxito.
    """
    form_class = PasswordChangingForm
    success_url = reverse_lazy('profile')

class UserAddRoleView(LoginRequiredMixin, FormView):
    template_name = 'members/add_role.html'
    form_class = UserAddRoleForm
    success_url = reverse_lazy('success_url_name')  # Cambia esto a la URL de éxito deseada

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Añade los roles disponibles al contexto de la plantilla.

        Parameters:
        -----------
        **kwargs : dict
            Argumentos adicionales de palabras clave.

        Returns:
        --------
        dict
            El contexto actualizado con los roles disponibles.
        """
        context = super().get_context_data(**kwargs)
        roles = Group.objects.exclude(name__icontains='administrador')
        context['roles'] = roles
        return context

    def form_valid(self, form):
        """
        Asignar el rol al usuario y redirigir a la URL de éxito si el formulario es válido.

        Args:
            form (AddRoleForm): El formulario utilizado para agregar un rol a un usuario.

        Returns:
            HttpResponse: La respuesta HTTP después de procesar el formulario.
        """
        user = self.request.user
        group = form.cleaned_data['group']

        if group == 'already_has_role':
            messages.error(self.request, "Ya tienes el rol seleccionado. Por favor, elige otro.")
            return self.form_invalid(form)
        
        user.groups.add(group)

        # Desactivar todos los permisos del grupo para el usuario
        for permission in group.permissions.all():
            user.user_permissions.remove(permission)

        messages.success(self.request, f"Se ha agregado el rol de {group.name} al usuario {user.username}, pero todos los permisos están desactivados por defecto.")
        return redirect('posts')

    def form_invalid(self, form):
        if not form.cleaned_data.get('group'):
            messages.error(self.request, "Por favor, seleccione un rol antes de enviar.")
        return super().form_invalid(form)
    
class UserNotificationsView(LoginRequiredMixin, TemplateView):
    """
    Vista para manejar las notificaciones de usuario.
    Esta vista requiere que el usuario esté autenticado y extiende de TemplateView.
    Atributos:
        template_name (str): Nombre de la plantilla HTML a renderizar.
    Métodos:
        get_context_data(**kwargs):
            Obtiene el contexto para renderizar la plantilla.
            Combina las categorías compradas y suscritas del miembro.
            Añade las notificaciones adicionales al contexto.
        post(request, *args, **kwargs):
            Maneja las solicitudes POST para alternar las notificaciones.
            Permite activar o desactivar notificaciones para categorías específicas
            o notificaciones adicionales.
    """
    template_name = 'members/notifications.html'

    def get_context_data(self, **kwargs):
        """
        Obtiene el contexto adicional para la vista.
        Este método extiende el contexto proporcionado por la clase base con información adicional
        específica del usuario actual, incluyendo categorías compradas y suscritas, y notificaciones.
        Args:
            **kwargs: Argumentos adicionales pasados al método.
        Returns:
            dict: Un diccionario que contiene el contexto extendido con las siguientes claves:
                - 'combined_categories': Lista combinada de categorías compradas y suscritas por el usuario.
                - 'purchased_categories': Categorías compradas por el usuario.
                - 'suscribed_categories': Categorías suscritas por el usuario.
                - 'notification': Objeto de notificación asociado al usuario.
                - 'additional_notifications': Notificaciones adicionales obtenidas del método del modelo de notificación.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        member = get_object_or_404(Member, id=user.id)
        
        # Try to get the Notification object, create if it doesn't exist
        notification, _ = Notification.objects.get_or_create(user=member)

        # Combine purchased and subscribed categories
        purchased_categories = member.purchased_categories.all()
        suscribed_categories = member.suscribed_categories.all()
        combined_categories = list(purchased_categories) + list(suscribed_categories)

        context['combined_categories'] = combined_categories
        context['purchased_categories'] = purchased_categories
        context['suscribed_categories'] = suscribed_categories
        context['notification'] = notification

        # Add additional notifications from the model method
        context['additional_notifications'] = notification.get_additional_notifications()

        return context

    def post(self, request, *args, **kwargs):
        """
        Maneja la solicitud POST para alternar las notificaciones de un usuario.
        Args:
            request (HttpRequest): La solicitud HTTP que contiene los datos POST.
            *args: Argumentos adicionales.
            **kwargs: Palabras clave adicionales.
        Funcionalidad:
            - Obtiene el usuario actual de la solicitud.
            - Intenta obtener el objeto Notification asociado al usuario, o lo crea si no existe.
            - Procesa la acción 'toggle_notification' para alternar las notificaciones de categorías
              o notificaciones adicionales según los datos POST recibidos.
            - Guarda los cambios en el objeto Notification.
            - Redirige a la vista de notificaciones.
        Datos POST:
            - action (str): La acción a realizar, en este caso 'toggle_notification'.
            - category_id (str): El ID de la categoría a alternar (opcional).
            - additional_notification (str): Notificación adicional a alternar (opcional).
        Returns:
            HttpResponseRedirect: Redirige a la vista de notificaciones.
        """
        user = self.request.user
        member = get_object_or_404(Member, id=user.id)
        
        # Try to get the Notification object, create if it doesn't exist
        notification, _ = Notification.objects.get_or_create(user=member)

        action = request.POST.get('action')
        category_id = request.POST.get('category_id')
        additional_notification = request.POST.get('additional_notification')

        if action == 'toggle_notification':
            if category_id:
                category = get_object_or_404(Category, id=category_id)
                if category in notification.notifications.all():
                    notification.notifications.remove(category)
                else:
                    notification.notifications.add(category)
            elif additional_notification:
                additional_notifications = notification.get_additional_notifications()
                if additional_notification in additional_notifications:
                    if additional_notification in notification.additional_notifications:
                        notification.additional_notifications.remove(additional_notification)
                    else:
                        notification.additional_notifications.append(additional_notification)
            notification.save()

        return redirect('notifications')