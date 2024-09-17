from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
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
    """
    Formulario para editar miembros.

    Este formulario permite editar la información de un miembro existente.
    Hereda de `UserChangeForm` y utiliza el modelo `Member`.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo y los campos del formulario.
    """
    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        """
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

class GroupEditForm(forms.ModelForm):
    """
    Formulario para editar un grupo y sus permisos.

    Campos:
        - permissions: Campo de selección múltiple para los permisos del grupo, representado como una lista de casillas de verificación.
    
    Meta:
        - model: El modelo Group que se va a editar.
        - fields: Los campos del modelo que se incluirán en el formulario.
        - labels: Etiquetas personalizadas para los campos del formulario.
    """
    
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(), 
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
        Guarda el grupo y sus permisos asociados.

        Args:
            commit: Booleano que indica si se debe guardar el grupo en la base de datos inmediatamente.

        Returns:
            El grupo guardado con sus permisos actualizados.
        """
        group = super().save(commit=False)
        if commit:
            group.save()
            group.permissions.set(self.cleaned_data['permissions'])
        return group

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
    """
    Formulario para registrar nuevos miembros.

    Este formulario permite registrar nuevos miembros solicitando un nombre de usuario,
    nombre, apellido, correo electrónico y contraseña. Verifica que las contraseñas coincidan
    y asigna al nuevo usuario al grupo 'suscriptor'.

    Atributos:
    ----------
    password1 : forms.CharField
        Campo para la contraseña.
    password2 : forms.CharField
        Campo para confirmar la contraseña.

    Métodos:
    --------
    clean_password2():
        Verifica que las contraseñas coincidan.
    save(commit=True):
        Guarda el nuevo usuario y lo asigna al grupo 'suscriptor'.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : tuple
            Campos que se incluirán en el formulario.
        labels : dict
            Etiquetas personalizadas para los campos del formulario.
        """
        model = Member
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': _('Nombre de usuario'),
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'email': _('Correo electrónico'),
        }

    def clean_password2(self):
        """
        Verifica que las contraseñas coincidan.

        Lanza una excepción de validación si las contraseñas no coinciden.

        Returns:
        --------
        str
            La segunda contraseña validada.
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        """
        Guarda el nuevo usuario y lo asigna al grupo 'suscriptor'.

        Si `commit` es True, guarda el usuario en la base de datos y le asigna
        todos los permisos del grupo 'suscriptor'.

        Parameters:
        -----------
        commit : bool, optional
            Si es True, guarda el usuario en la base de datos (por defecto es True).

        Returns:
        --------
        Member
            El nuevo usuario registrado.
        """
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
    """
    Formulario para registrar nuevos miembros.

    Este formulario permite registrar nuevos miembros solicitando un nombre de usuario,
    nombre, apellido, correo electrónico y contraseña. Verifica que las contraseñas coincidan
    y asigna al nuevo usuario a un rol específico.

    Atributos:
    ----------
    password1 : forms.CharField
        Campo para la contraseña.
    password2 : forms.CharField
        Campo para confirmar la contraseña.

    Métodos:
    --------
    __init__(*args, **kwargs):
        Inicializa el formulario y añade el campo de rol.
    clean_password2():
        Verifica que las contraseñas coincidan.
    save(commit=True):
        Guarda el nuevo usuario y lo asigna al rol seleccionado.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : tuple
            Campos que se incluirán en el formulario.
        labels : dict
            Etiquetas personalizadas para los campos del formulario.
        """
        model = Member
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': _('Nombre de usuario'),
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'email': _('Correo electrónico'),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y añade el campo de rol.

        Parameters:
        -----------
        *args : list
            Argumentos posicionales.
        **kwargs : dict
            Argumentos de palabras clave.
        """
        super(MemberJoinForm, self).__init__(*args, **kwargs)
        self.fields['role'] = forms.ModelChoiceField(
            queryset=Group.objects.exclude(name='suscriptor'),
            label='Rol',
            required=True
        )

    def clean_password2(self):
        """
        Verifica que las contraseñas coincidan.

        Lanza una excepción de validación si las contraseñas no coinciden.

        Returns:
        --------
        str
            La segunda contraseña validada.
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        """
        Guarda el nuevo usuario y lo asigna al rol seleccionado.

        Si `commit` es True, guarda el usuario en la base de datos y le asigna
        todos los permisos del rol seleccionado.

        Parameters:
        -----------
        commit : bool, optional
            Si es True, guarda el usuario en la base de datos (por defecto es True).

        Returns:
        --------
        Member
            El nuevo usuario registrado.
        """
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
    Formulario de inicio de sesión para miembros.

    Este formulario permite a los miembros iniciar sesión utilizando su nombre de usuario
    y contraseña. Hereda de `AuthenticationForm` y utiliza el modelo `Member`.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo y los campos del formulario.
    """
    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        labels : dict
            Etiquetas personalizadas para los campos del formulario.
        """
        model = Member
        fields = ['username', 'password']
        labels = {
            'username': _('Nombre de usuario'),
            'password': _('Contraseña'),
        }
        
class MemberEditGroupForm(forms.ModelForm):
    """
    Formulario para editar los grupos (roles) de un miembro.

    Este formulario permite asignar o modificar los grupos (roles) de un miembro existente.
    Utiliza un campo de selección múltiple con casillas de verificación para elegir los grupos.

    Atributos:
    ----------
    groups : forms.ModelMultipleChoiceField
        Campo para seleccionar múltiples grupos (roles) utilizando casillas de verificación.

    Meta:
    -----
    model : Model
        El modelo que se utilizará para el formulario.
    fields : list
        Lista de campos que se incluirán en el formulario.
    """
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label = "Roles"
    )

    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        """
        model = Member
        fields = ['groups']
    
class MemberEditPermissionForm(forms.ModelForm):
    """
    Formulario para editar los permisos de un miembro.

    Este formulario permite asignar o modificar los permisos de un miembro existente.
    Utiliza un campo de selección múltiple con casillas de verificación para elegir los permisos.

    Atributos:
    ----------
    permissions : forms.ModelMultipleChoiceField
        Campo para seleccionar múltiples permisos utilizando casillas de verificación.

    Métodos:
    --------
    __init__(*args, **kwargs):
        Inicializa el formulario y ajusta el queryset y los permisos iniciales
        basados en los grupos del miembro.
    """
    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y ajusta el queryset y los permisos iniciales
        basados en los grupos del miembro.

        Parameters:
        -----------
        *args : list
            Argumentos posicionales.
        **kwargs : dict
            Argumentos de palabras clave.
        """
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
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        """
        model = Member
        fields = ['permissions']  


class MemberStatusForm(forms.ModelForm):
    """
    Formulario para editar el estado de actividad de un miembro.

    Este formulario permite activar o desactivar a un miembro utilizando un campo de casilla de verificación.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo, los campos, los widgets y las etiquetas del formulario.

    Métodos:
    --------
    __init__(*args, **kwargs):
        Inicializa el formulario y ajusta el sufijo de la etiqueta del campo 'is_active'.
    """
    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        widgets : dict
            Widgets personalizados para los campos del formulario.
        labels : dict
            Etiquetas personalizadas para los campos del formulario.
        """
        model = Member
        fields = ['is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_active': 'Activo',
        }
    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y ajusta el sufijo de la etiqueta del campo 'is_active'.

        Parameters:
        -----------
        *args : list
            Argumentos posicionales.
        **kwargs : dict
            Argumentos de palabras clave.
        """
        super(MemberStatusForm, self).__init__(*args, **kwargs)
        self.fields['is_active'].label_suffix = ''

class MemberListForm(forms.Form):
    """
    Formulario que lista todos los miembros del sistema.

    Campos:
        - users: Campo de selección de un solo miembro.
    """
    users = forms.ModelChoiceField(queryset=Member.objects.all(), label="Miembros", required=True)

class EditProfileForm(UserChangeForm):
    """
    Formulario para editar el perfil de un usuario.

    Campos:
        email: Campo de correo electrónico con un widget de entrada de correo electrónico.
        first_name: Campo de nombre con un widget de entrada de texto.
        last_name: Campo de apellido con un widget de entrada de texto.
        username: Campo de nombre de usuario con un widget de entrada de texto.
        password: Campo de contraseña oculto, no requerido.

    Meta:
        model: Modelo asociado al formulario (Member).
        fields: Campos que se incluirán en el formulario.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Correo electrónico'
    )
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombre'
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Apellido'
    )
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Usuario'
    )
    password = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Member
        fields = ( 'username', 'first_name', 'last_name', 'email', 'password')

class PasswordChangingForm(PasswordChangeForm):
    """
    Formulario personalizado para cambiar la contraseña del usuario.

    Atributos:
        old_password: Campo para ingresar la contraseña actual del usuario.
        new_password1: Campo para ingresar la nueva contraseña del usuario.
        new_password2: Campo para confirmar la nueva contraseña del usuario.

    Meta:
        model: El modelo asociado con este formulario (Member).
        fields: Los campos que se incluirán en el formulario ('old_password', 'new_password1', 'new_password2').
    """
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
        label='Contraseña actual'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
        label='Nueva contraseña'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}),
        label='Confirmar nueva contraseña'
    )

    class Meta:
        model = Member
        fields = ('old_password', 'new_password1', 'new_password2')