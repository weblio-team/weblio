from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Member
from django import forms


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
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        label="Permisos",
        required=False,
        widget=forms.CheckboxSelectMultiple  # Permite seleccionar múltiples permisos con checkboxes
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']

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

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            suscriptor_group = Group.objects.get(name='suscriptor')
            user.groups.add(suscriptor_group)
        return user
    
class MemberJoinForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = Member
        fields = ('username', 'first_name', 'last_name', 'email')

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
        if commit:
            user.save()
            role = self.cleaned_data['role']
            user.groups.add(role)
        return user

class MemberLoginForm(AuthenticationForm):
    """
    Formulario de autenticación para iniciar sesión en el sistema.
    """
    class Meta:
        model = Member
        fields = ['username', 'password']
        
class MemberEditGroupForm(forms.ModelForm):
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
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),  # Inicialmente vacío
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Permisos"
    )
    is_active = forms.BooleanField(required=False, label="Activo")

    class Meta:
        model = Member
        fields = ['permissions', 'is_active']

    def __init__(self, *args, **kwargs):
        member = kwargs.get('instance')
        super(MemberEditPermissionForm, self).__init__(*args, **kwargs)
        if member:
            self.fields['permissions'].queryset = Permission.objects.filter(group__user=member).distinct()


class MemberStatusForm(forms.ModelForm):
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
