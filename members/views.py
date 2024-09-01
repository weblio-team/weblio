from django.views.generic import FormView, TemplateView,  CreateView
from django.urls import reverse_lazy

from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from .models import Member
from django.views import View
from django.views.generic import CreateView
from django.shortcuts import render, get_object_or_404, redirect

from .forms import GroupListForm, CreateGroupForm
from .models import Member
from .forms import MemberRegisterForm, MemberJoinForm, MemberEditForm, MemberLoginForm
from .forms import RoleListForm, RoleCreateForm


class MemberListView(TemplateView):
    """
    Vista para listar todos los miembros con su grupo y permisos.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.

    Métodos:
        get_context_data(**kwargs): Agrega los miembros con sus grupos y permisos al contexto de la plantilla.
        post(request, *args, **kwargs): Maneja la selección de un miembro y redirige a la página de edición.
    """
    template_name = 'members/member_list.html'

    def get_context_data(self, **kwargs):
        """
        Agrega los miembros con sus grupos y permisos al contexto de la plantilla.

        Returns:
            dict: Contexto con los miembros, grupos y permisos.
        """
        context = super().get_context_data(**kwargs)
        members = Member.objects.all().prefetch_related('groups', 'user_permissions')
        context['members'] = members
        return context

    def post(self, request, *args, **kwargs):
        """
        Maneja la selección de un miembro y redirige a la página de edición.

        Args:
            request (HttpRequest): El objeto de la solicitud HTTP.

        Returns:
            HttpResponse: Redirige a la vista de edición del miembro seleccionado.
        """
        selected_member_id = request.POST.get('selected_member')
        if selected_member_id:
            return redirect('member-edit', pk=selected_member_id)
        return self.get(request, *args, **kwargs)


class GroupListView(TemplateView):
    """
    Vista para listar todos los grupos junto con sus permisos.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.

    Métodos:
        get_context_data(**kwargs): Agrega los grupos con sus permisos al contexto de la plantilla.
        form_valid(form): Procesa el formulario cuando es válido.
        form_invalid(form): Procesa el formulario cuando es inválido.
    """
    template_name = 'groups/group_list.html'

    def get_context_data(self, **kwargs):
        """
        Agrega los grupos con sus permisos al contexto de la plantilla.

        Returns:
            dict: Contexto con los grupos y permisos.
        """
        context = super().get_context_data(**kwargs)
        groups = Group.objects.all().prefetch_related('permissions')
        context['groups'] = groups
        return context

    def form_valid(self, form):
        """
        Procesa el formulario cuando es válido.

        Args:
            form (GroupListForm): El formulario que ha sido validado.

        Returns:
            HttpResponse: Respuesta con el contexto actualizado con los permisos del grupo seleccionado.
        """
        group_id = form.cleaned_data['group'].id
        group = Group.objects.get(id=group_id)
        permissions = group.permissions.all()
        
        # Pasar los permisos al contexto de la plantilla
        context = self.get_context_data(form=form, permissions=permissions)
        return self.render_to_response(context)
    
    def form_invalid(self, form):
        """
        Procesa el formulario cuando es inválido.

        Args:
            form (GroupListForm): El formulario inválido.

        Returns:
            HttpResponse: Respuesta con el contexto de la plantilla, sin permisos.
        """
        context = self.get_context_data(form=form, permissions=None)
        return self.render_to_response(context)


class CreateGroupView(FormView):
    """
    Vista para crear un nuevo grupo y asignarle permisos.

    Muestra un formulario que permite ingresar un nombre para el nuevo grupo
    y asignarle múltiples permisos.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.
        form_class (class): Clase del formulario que se utiliza en la vista.
        success_url (str): URL a la que se redirige después de que el formulario es válido.

    Métodos:
        form_valid(form): Método que se ejecuta cuando el formulario es válido y guarda el nuevo grupo.
    """
    template_name = 'groups/group_create.html'
    form_class = CreateGroupForm
    success_url = reverse_lazy('group-list')

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
        return super().form_valid(form)


class MemberEditView(View):
    """
    Vista para editar el grupo y permisos de un miembro.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.

    Métodos:
        get(request, pk): Obtiene los detalles del miembro y los renderiza en la plantilla.
        post(request, pk): Procesa las modificaciones de grupo y permisos y redirige a la lista de miembros.
    """
    template_name = 'members/member_edit.html'

    def get(self, request, pk):
        """
        Obtiene los detalles del miembro y los renderiza en la plantilla.

        Args:
            request (HttpRequest): El objeto de la solicitud HTTP.
            pk (int): La clave primaria del miembro.

        Returns:
            HttpResponse: Renderiza la plantilla con los detalles del miembro.
        """
        member = get_object_or_404(Member, pk=pk)
        groups = Group.objects.all()
        selected_group = member.groups.first()
        permissions = selected_group.permissions.all() if selected_group else []

        context = {
            'member': member,
            'groups': groups,
            'selected_group': selected_group,
            'permissions': permissions,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        """
        Procesa las modificaciones de grupo y permisos y redirige a la lista de miembros.

        Args:
            request (HttpRequest): El objeto de la solicitud HTTP.
            pk (int): La clave primaria del miembro.

        Returns:
            HttpResponse: Redirige a la lista de miembros después de guardar los cambios.
        """
        member = get_object_or_404(Member, pk=pk)
        group_id = request.POST.get('group')
        selected_group = Group.objects.get(id=group_id)

        # Actualizar grupo del miembro
        member.groups.clear()
        member.groups.add(selected_group)

        # Actualizar permisos según el checkbox
        selected_permissions = request.POST.getlist('permissions')
        member.user_permissions.clear()
        member.user_permissions.add(*selected_permissions)

        # Redirigir a la lista de miembros después de guardar los cambios
        return redirect('member-list')
    
class RoleListView(TemplateView):
    """
    Vista para listar todos los grupos junto con sus permisos.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.

    Métodos:
        get_context_data(**kwargs): Agrega los grupos con sus permisos al contexto de la plantilla.
        form_valid(form): Procesa el formulario cuando es válido.
        form_invalid(form): Procesa el formulario cuando es inválido.
    """
    template_name = 'groups/group_list.html'

    def get_context_data(self, **kwargs):
        """
        Agrega los grupos con sus permisos al contexto de la plantilla.

        Returns:
            dict: Contexto con los grupos y permisos.
        """
        context = super().get_context_data(**kwargs)
        groups = Group.objects.all().prefetch_related('permissions')
        context['groups'] = groups
        return context

    def form_valid(self, form):
        """
        Procesa el formulario cuando es válido.

        Args:
            form (GroupListForm): El formulario que ha sido validado.

        Returns:
            HttpResponse: Respuesta con el contexto actualizado con los permisos del grupo seleccionado.
        """
        group_id = form.cleaned_data['group'].id
        group = Group.objects.get(id=group_id)
        permissions = group.permissions.all()
        
        # Pasar los permisos al contexto de la plantilla
        context = self.get_context_data(form=form, permissions=permissions)
        return self.render_to_response(context)
    
    def form_invalid(self, form):
        """
        Procesa el formulario cuando es inválido.

        Args:
            form (GroupListForm): El formulario inválido.

        Returns:
            HttpResponse: Respuesta con el contexto de la plantilla, sin permisos.
        """
        context = self.get_context_data(form=form, permissions=None)
        return self.render_to_response(context)


class RoleCreateView(FormView):
    """
    Vista para crear un nuevo grupo y asignarle permisos.

    Muestra un formulario que permite ingresar un nombre para el nuevo grupo
    y asignarle múltiples permisos.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.
        form_class (class): Clase del formulario que se utiliza en la vista.
        success_url (str): URL a la que se redirige después de que el formulario es válido.

    Métodos:
        form_valid(form): Método que se ejecuta cuando el formulario es válido y guarda el nuevo grupo.
    """
    template_name = 'groups/group_create.html'
    form_class = RoleCreateForm
    success_url = reverse_lazy('group-list')

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
        return super().form_valid(form)


class MemberListView(TemplateView):
    """
    Vista para listar todos los miembros con su grupo y permisos.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.

    Métodos:
        get_context_data(**kwargs): Agrega los miembros con sus grupos y permisos al contexto de la plantilla.
        post(request, *args, **kwargs): Maneja la selección de un miembro y redirige a la página de edición.
    """
    template_name = 'members/member_list.html'

    def get_context_data(self, **kwargs):
        """
        Agrega los miembros con sus grupos y permisos al contexto de la plantilla.

        Returns:
            dict: Contexto con los miembros, grupos y permisos.
        """
        context = super().get_context_data(**kwargs)
        members = Member.objects.all().prefetch_related('groups', 'user_permissions')
        context['members'] = members
        return context

    def post(self, request, *args, **kwargs):
        """
        Maneja la selección de un miembro y redirige a la página de edición.

        Args:
            request (HttpRequest): El objeto de la solicitud HTTP.

        Returns:
            HttpResponse: Redirige a la vista de edición del miembro seleccionado.
        """
        selected_member_id = request.POST.get('selected_member')
        if selected_member_id:
            return redirect('member-edit', pk=selected_member_id)
        return self.get(request, *args, **kwargs)


class MemberEditView(View):
    """
    Vista para editar el grupo y permisos de un miembro.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.

    Métodos:
        get(request, pk): Obtiene los detalles del miembro y los renderiza en la plantilla.
        post(request, pk): Procesa las modificaciones de grupo y permisos y redirige a la lista de miembros.
    """
    template_name = 'members/member_edit.html'

    def get(self, request, pk):
        """
        Obtiene los detalles del miembro y los renderiza en la plantilla.

        Args:
            request (HttpRequest): El objeto de la solicitud HTTP.
            pk (int): La clave primaria del miembro.

        Returns:
            HttpResponse: Renderiza la plantilla con los detalles del miembro.
        """
        member = get_object_or_404(Member, pk=pk)
        groups = Group.objects.all()
        selected_group = member.groups.first()
        permissions = selected_group.permissions.all() if selected_group else []

        context = {
            'member': member,
            'groups': groups,
            'selected_group': selected_group,
            'permissions': permissions,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        """
        Procesa las modificaciones de grupo y permisos y redirige a la lista de miembros.

        Args:
            request (HttpRequest): El objeto de la solicitud HTTP.
            pk (int): La clave primaria del miembro.

        Returns:
            HttpResponse: Redirige a la lista de miembros después de guardar los cambios.
        """
        member = get_object_or_404(Member, pk=pk)
        group_id = request.POST.get('group')
        selected_group = Group.objects.get(id=group_id)

        # Actualizar grupo del miembro
        member.groups.clear()
        member.groups.add(selected_group)

        # Actualizar permisos según el checkbox
        selected_permissions = request.POST.getlist('permissions')
        member.user_permissions.clear()
        member.user_permissions.add(*selected_permissions)

        # Redirigir a la lista de miembros después de guardar los cambios
        return redirect('member-list')


class MemberRegisterView(CreateView):
    """
    Vista para manejar el formulario de registro. La cuenta se crea con el rol de 
    "suscriptor" y se activa automáticamente.
    """
    model = Member
    form_class = MemberRegisterForm
    template_name = 'members/member_register.html'
    success_url = reverse_lazy('member-login')


class MemberLoginView(LoginView):
    """
    Vista para manejar el formulario de inicio de sesión.
    """
    form_class = MemberLoginForm
    template_name = 'members/member_login.html'

    def get_success_url(self):
        """
        Devuelve la URL a la que redirigir después de iniciar sesión.
        """
        return reverse_lazy('posts')  # Ensure 'posts' matches the URL pattern name


class MemberJoinView(CreateView):
    """
    Vista para manejar el formulario de unirse al sistema. El usuario selecciona un rol 
    (grupo de Django) y la cuenta se crea desactivada inicialmente.
    """
    model = Member
    form_class = MemberJoinForm
    template_name = 'members/member_join.html'
    success_url = reverse_lazy('member-login')
