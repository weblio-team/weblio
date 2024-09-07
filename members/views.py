from pyexpat.errors import messages
from django.views.generic import FormView, TemplateView,  CreateView
from django.urls import reverse_lazy

from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from .models import Member
from django import views
from django.views.generic import CreateView
from django.shortcuts import render, get_object_or_404, redirect

from .forms import CreateGroupForm, MemberEditGroupForm, MemberEditPermissionForm, MemberStatusForm
from .models import Member
from .forms import MemberRegisterForm, MemberJoinForm, MemberLoginForm
from django.contrib import messages
from django.http import HttpResponseRedirect 
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin


class HomeView(TemplateView):
    """
    Vista de la página de inicio.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.
    """
    template_name = 'home.html'


# views for groups
class GroupListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Vista para listar todos los grupos junto con sus permisos.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.
        permission_required (list): Lista de permisos requeridos para acceder a la vista.

    Métodos:
        get_context_data(**kwargs): Agrega los grupos con sus permisos al contexto de la plantilla.
        form_valid(form): Procesa el formulario cuando es válido.
        form_invalid(form): Procesa el formulario cuando es inválido.
    """
    template_name = 'groups/group_list.html'
    permission_required = ['auth.view_group',]

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

# views for members
class MemberListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Vista para listar todos los miembros con su grupo y permisos.

    Atributos:
        template_name (str): Ruta del template que se utiliza para renderizar la vista.
        permission_required (list): Lista de permisos requeridos para acceder a la vista.

    Métodos:
        get_context_data(**kwargs): Agrega los miembros con sus grupos y permisos al contexto de la plantilla.
        post(request, *args, **kwargs): Maneja la selección de un miembro y redirige a la página de edición.
    """
    template_name = 'members/member_list.html'
    permission_required = ['auth.view_member',
        ]

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

    permission_required = ['auth.change_member',
        ]

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
        return render(request, 'members/edit_group.html', {'form': form, 'member': member})

    def post(self, request, pk):
        """
        Actualiza los grupos de un miembro y sus permisos asociados.
        Parámetros:
        - request: La solicitud HTTP recibida.
        - pk: El ID del miembro a editar.
        Retorna:
        - Una respuesta HTTP redirigiendo a la lista de miembros si la actualización es exitosa,
          o una respuesta HTTP con el formulario de edición de grupos y el miembro en caso contrario.
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
            
            # Asignar permisos de los nuevos grupos
            for group in new_groups:
                member.user_permissions.add(*group.permissions.all())
            
            return redirect('member-list')
        return render(request, 'members/edit_group.html', {'form': form, 'member': member})
    

class MemberEditPermissionView(LoginRequiredMixin, PermissionRequiredMixin, views.View):
    """
    Vista de edición de permisos de miembro.
    Esta vista permite editar los permisos de un miembro específico.
    Se espera que se proporcione un ID de miembro válido como parámetro de ruta.

    Atributos:
        permission_required: Lista de permisos requeridos para acceder a esta vista.
    
    Métodos:
        get(request, pk): Obtiene el formulario de edición de permisos y los permisos actuales del miembro.
        post(request, pk): Guarda los cambios realizados en el formulario de edición de permisos.
    """

    permission_required = ['auth.change_member',
        ]
    
    def get(self, request, pk):
        """
        Obtiene el formulario de edición de permisos y los permisos actuales del miembro.
        Parámetros:
        - request: La solicitud HTTP recibida.
        - pk: El ID del miembro a editar.
        Retorna:
        - Una respuesta HTTP que renderiza la plantilla 'members/edit_permission.html' con el formulario, el miembro y los permisos actuales.
        """
        member = get_object_or_404(Member, pk=pk)
        form = MemberEditPermissionForm(instance=member)
        user_permissions = member.user_permissions.all()
        return render(request, 'members/edit_permission.html', {
            'form': form,
            'member': member,
            'user_permissions': user_permissions
        })

    def post(self, request, pk):
        """
        Guarda los cambios realizados en el formulario de edición de permisos.
        Parámetros:
        - request: La solicitud HTTP recibida.
        - pk: El ID del miembro a editar.
        Retorna:
        - Una respuesta HTTP que redirige a la vista 'member-list' si los cambios se guardaron correctamente.
        - Una respuesta HTTP que renderiza la plantilla 'members/edit_permission.html' con el formulario, el miembro y los permisos actuales si hay errores en el formulario.
        """
        member = get_object_or_404(Member, pk=pk)
        form = MemberEditPermissionForm(request.POST, instance=member)
        if form.is_valid():
            member = form.save(commit=False)
            member.save()  # Guardar el objeto Member primero
            member.user_permissions.set(form.cleaned_data['permissions'])
            return redirect('member-list')
        return render(request, 'members/edit_permission.html', {
            'form': form,
            'member': member,
            'user_permissions': member.user_permissions.all()
        })


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
            form.save()
            return redirect('member-list')
        return render(request, self.template_name, {'form': form, 'member': member})
    

class MemberRegisterView(CreateView):
    form_class = MemberRegisterForm
    template_name = 'members/member_register.html'
    success_url = reverse_lazy('member-login')


class MemberLoginView(LoginView):
    """
    Vista para manejar el formulario de inicio de sesión.
    """
    form_class = MemberLoginForm
    template_name = 'members/member_login.html'


    def form_invalid(self, form):
        """
        Metodo que se llama tras el POST del form con datos invalidos.
        """
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        self.user = authenticate(self.request, username=username, password=password)
        if self.user is not None:
            if not self.user.is_active:
                messages.info(self.request, "Su cuenta está inactiva. Por favor, contacte al administrador para más detalles.")
                return HttpResponseRedirect(reverse_lazy('login')) 
        else:
            messages.error(self.request, "Error en el nombre de usuario o contraseña. Por favor, intente de nuevo.")
        return super().form_invalid(form)
    
    def get_success_url(self):
        """
        Devuelve la URL a la que redirigir después de iniciar sesión.
        """
        return reverse_lazy('posts')  
    

class MemberJoinView(CreateView):
    """
    Vista para manejar el formulario de unirse al sistema. El usuario selecciona un rol 
    (grupo de Django) y la cuenta se crea desactivada inicialmente.
    """
    form_class = MemberJoinForm
    template_name = 'members/member_join.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        """
        Agrega los roles al contexto, excluyendo el rol 'suscriptor'.
        """
        context = super().get_context_data(**kwargs)
        roles = Group.objects.exclude(name='suscriptor')
        context['roles'] = roles
        return context


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