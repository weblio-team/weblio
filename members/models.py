from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import MemberManager


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

    Atributos de clase:
        - USERNAME_FIELD (str): Define el campo que se usa como identificador único (email).
        - REQUIRED_FIELDS (list): Lista de campos obligatorios para el usuario, además de USERNAME_FIELD.
        - objects (MemberManager): El gestor de modelos personalizado para manejar la creación de usuarios y superusuarios.

    Métodos:
        - __str__(): Retorna el email del usuario como representación en cadena.
    """

    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = MemberManager()

    def __str__(self):
        """
        Retorna la representación en cadena del usuario.

        Retorna:
            - str: El email del usuario.
        """
        return self.email
