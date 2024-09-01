from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from .managers import MemberManager

def get_default_group():
    try:
        return Group.objects.get(name='suscriptor')
    except ObjectDoesNotExist:
        # Handle the case where the default group does not exist
        # You might want to create it or handle it differently
        return None  # or raise an exception, or create the group

class Member(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario personalizado donde el email es el identificador único
    para la autenticación.

    Hereda de:
        - AbstractBaseUser: Proporciona las implementaciones principales para un modelo de usuario.
        - PermissionsMixin: Agrega campos y métodos de permisos al modelo de usuario.

    Atributos:
        - email (EmailField): Dirección de email del usuario. Es el identificador único.
        - is_staff (BooleanField): Indica si el usuario puede acceder al sitio de administración.
        - is_active (BooleanField): Indica si el usuario está activo.
        - date_joined (DateTimeField): La fecha y hora en que el usuario se unió.
        - group (ForeignKey): El singular rol al cual el usuario pertenece.

    Atributos de clase:
        - USERNAME_FIELD (str): Define el campo que se usa como identificador único (email).
        - REQUIRED_FIELDS (list): Lista de campos obligatorios para el usuario, además de USERNAME_FIELD.
        - objects (MemberManager): El gestor de modelos personalizado para manejar la creación de usuarios y superusuarios.

    Métodos:
        - __str__(): Retorna el email del usuario como representación en cadena.
    """

    username = models.CharField(max_length=150, unique=True, default = '')
    first_name = models.CharField(_('first name'), max_length=30, default = '')
    last_name = models.CharField(_('last name'), max_length=150, default = '')
    email = models.EmailField(_('email address'), unique=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    group = models.ForeignKey(
        Group,
        verbose_name=_('group'),
        on_delete=models.SET_DEFAULT,
        default = get_default_group,  
        related_name='members',
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email' ,'first_name', 'last_name']

    objects = MemberManager()

    class Meta:
        verbose_name = _('member')
        verbose_name_plural = _('members')

        permissions = [
        
        ]

    def __str__(self):
        """
        Retorna la representación en cadena del usuario.

        Retorna:
            - str: El email del usuario.
        """
        return self.email
