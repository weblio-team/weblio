from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Member
from django import forms
from django.db.models import Q
from django.utils.translation import gettext as _


class MemberCreationForm(UserCreationForm):
    """
    Formulario para la creación de un nuevo miembro.

    Hereda de:
        - UserCreationForm: Formulario estándar de Django para la creación de usuarios.

    Meta:
        - model: El modelo `Member` al que está vinculado el formulario.
        - fields: Campos que se utilizarán en el formulario.
    """

    class Meta:
        model = Member
        fields = ("email",)
        labels = {
            'email': _('Correo electrónico'),
        }
        
class MemberEditForm(UserChangeForm):
    class Meta:
        model = Member
        fields = ['email', 'password', 'is_staff', 'is_active', 'groups', 'user_permissions']


class MemberChangeForm(UserChangeForm):
    """
    Formulario para la actualización de un miembro existente.

    Hereda de:
        - UserChangeForm: Formulario estándar de Django para la edición de usuarios.

    Meta:
        - model: El modelo `Member` al que está vinculado el formulario.
        - fields: Campos que se utilizarán en el formulario.
    """

    class Meta:
        model = Member
        fields = ("email",)
        labels = {
            'email': _('Correo electrónico'),
        }


class UserListForm(forms.Form):
    """
    Formulario que lista todos los miembros del sistema.

    Campos:
        - users: Campo de selección de un solo miembro.
    """
    users = forms.ModelChoiceField(queryset=Member.objects.all(), label="Miembros", required=True)


class GroupListForm(forms.Form):
    """
    Formulario que lista todos los grupos junto con sus permisos.

    Campos:
        - group: Campo de selección de un grupo.
        - permissions: Campo de selección múltiple de permisos.
    """
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label="Grupos", required=True)
    permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), label="Permisos", required=False)


class CreateGroupForm(forms.ModelForm):
    """
    Formulario para crear un nuevo grupo y asignarle permisos.

    Campos:
        - name: Nombre del grupo.
        - permissions: Campo de selección múltiple de permisos.

    Hereda de:
        - forms.ModelForm: Formulario basado en un modelo estándar de Django.

    Meta:
        - model: El modelo `Group` al que está vinculado el formulario.
        - fields: Campos que se utilizarán en el formulario.

    Métodos:
        - save(commit=True): Guarda el grupo y asigna los permisos seleccionados.
    """
    from django.db.models import Q

    permissions = forms.ModelMultipleChoiceField(
    queryset=Permission.objects.filter(
        Q(name__iregex='.*member.*') |
        Q(name__iregex='.*category.*') |
        Q(name__iregex='.*post.*') |
        Q(name__iregex='.*group.*') |
        Q(name__iregex='.*permission.*') |
        Q(name__iregex='.*publish.*')
    ),
    label="Permisos",
    required=False,
    widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        labels = {
            'name': _('Nombre'),
            'permissions': _('Permisos'),
        }

    def save(self, commit=True):
        """
        Guarda el grupo y asigna los permisos seleccionados.

        Parámetros:
            - commit (bool): Booleano que indica si se debe guardar el grupo inmediatamente.

        Retorna:
            - Group: El objeto grupo creado o actualizado.
        """
        group = super().save(commit=False)
        if commit:
            group.save()
            group.permissions.set(self.cleaned_data['permissions'])
        return group

class MemberRegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = Member
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': _('Nombre de usuario'),
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'email': _('Correo electrónico'),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True  # Activar al usuario
        if commit:
            user.save()
            suscriptor_group = Group.objects.get(name='suscriptor')
            user.groups.add(suscriptor_group)
            # Asignar todos los permisos del grupo "suscriptor" al usuario
            permissions = suscriptor_group.permissions.all()
            user.user_permissions.set(permissions)
        return user
    
class MemberJoinForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = Member
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': _('Nombre de usuario'),
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'email': _('Correo electrónico'),
        }

    def __init__(self, *args, **kwargs):
        super(MemberJoinForm, self).__init__(*args, **kwargs)
        self.fields['role'] = forms.ModelChoiceField(
            queryset=Group.objects.exclude(name='suscriptor'),
            label='Rol',
            required=True
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False  # Usuario inactivo por defecto
        if commit:
            user.save()
            role = self.cleaned_data['role']
            user.groups.add(role)
            # Asignar todos los permisos del rol seleccionado al usuario
            permissions = role.permissions.all()
            user.user_permissions.set(permissions)
        return user

class MemberLoginForm(AuthenticationForm):
    """
    Formulario de autenticación para iniciar sesión en el sistema.
    """
    class Meta:
        model = Member
        fields = ['username', 'password']
        labels = {
            'username': _('Nombre de usuario'),
            'password': _('Contraseña'),
        }
        
class MemberEditGroupForm(forms.ModelForm):
    """
    Formulario para editar los roles de un miembro.

    Campos:
        - groups: Campo de selección múltiple para los roles del miembro.
    """
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label = "Roles"
    )

    class Meta:
        model = Member
        fields = ['groups']
    
class MemberEditPermissionForm(forms.ModelForm):
    """
    Formulario para editar los permisos de un miembro.

    Campos:
        - permissions: Campo de selección múltiple para los permisos.
    
    Métodos:
        - __init__: Configura el formulario inicializando el queryset de permisos disponibles
          basado en los grupos a los que el miembro pertenece. También establece los permisos
          que el miembro ya tiene como valores iniciales seleccionados en el formulario.
    """
    def __init__(self, *args, **kwargs):
        member = kwargs.get('instance')
        super(MemberEditPermissionForm, self).__init__(*args, **kwargs)
        if member:
            self.fields['permissions'].queryset = Permission.objects.filter(
                Q(group__in=member.groups.all())
            ).distinct()

            self.fields['permissions'].initial = member.user_permissions.all()

    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),  # Inicialmente vacío
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Permisos"
    )

    class Meta:
        model = Member
        fields = ['permissions']  


class MemberStatusForm(forms.ModelForm):
    """
    Formulario para editar el estado de activación de un miembro.

    Campos:
        - is_active: Campo de selección para activar o desactivar al miembro.
    
    Métodos:
        - __init__: Personaliza el campo 'is_active' para que no tenga un sufijo en la etiqueta.
    """
    class Meta:
        model = Member
        fields = ['is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_active': 'Activo',
        }
    def __init__(self, *args, **kwargs):
        super(MemberStatusForm, self).__init__(*args, **kwargs)
        self.fields['is_active'].label_suffix = ''

class MemberListForm(forms.Form):
    """
    Formulario que lista todos los miembros del sistema.

    Campos:
        - users: Campo de selección de un solo miembro.
    """
    users = forms.ModelChoiceField(queryset=Member.objects.all(), label="Miembros", required=True)

class RoleListForm(forms.Form):
    """
    Formulario que lista todos los grupos junto con sus permisos.

    Campos:
        - group: Campo de selección de un grupo.
        - permissions: Campo de selección múltiple de permisos.
    """
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label="Grupos", required=True)
    permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.all(), label="Permisos", required=False)

class RoleCreateForm(forms.ModelForm):
    """
    Formulario para crear un nuevo grupo y asignarle permisos.

    Campos:
        - name: Nombre del grupo.
        - permissions: Campo de selección múltiple de permisos.

    Hereda de:
        - forms.ModelForm: Formulario basado en un modelo estándar de Django.

    Meta:
        - model: El modelo `Group` al que está vinculado el formulario.
        - fields: Campos que se utilizarán en el formulario.

    Métodos:
        - save(commit=True): Guarda el grupo y asigna los permisos seleccionados.
    """
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all().filter(content_type__app_label__in=['members', 'posts']),
        label="Permisos",
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        labels = {
            'name': _('Nombre'),
            'permissions': _('Permisos'),
        }

    def save(self, commit=True):
        """
        Guarda el grupo y asigna los permisos seleccionados.

        Parámetros:
            - commit (bool): Booleano que indica si se debe guardar el grupo inmediatamente.

        Retorna:
            - Group: El objeto grupo creado o actualizado.
        """
        group = super().save(commit=False)
        if commit:
            group.save()
            group.permissions.set(self.cleaned_data['permissions'])
        return group
