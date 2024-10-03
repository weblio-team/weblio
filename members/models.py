from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
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
    pfp = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    purchased_categories = models.ManyToManyField('posts.Category', related_name='purchased_members', blank=True)
    suscribed_categories = models.ManyToManyField('posts.Category', related_name='suscribed_members', blank=True)


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email' ,'first_name', 'last_name']

    objects = MemberManager()

    class Meta:
        verbose_name = _('member')
        verbose_name_plural = _('members')

        permissions = [
            ('view_dashboard', 'Can view dashboard'),
            ('make_relevant', 'Can make a post relevant'),
        ]

    def __str__(self):
        """
        Retorna la representación en cadena del usuario.

        Retorna:
            - str: El username del usuario.
        """
        return self.username
    
    def get_pfp_url(self):
        if self.pfp:
            return self.pfp.url
        return 'https://picsum.photos/seed/picsum/1080'  # URL de imagen por defecto
    
class Notification(models.Model):
    """
    Clase Notification que representa las notificaciones de un usuario.
    Atributos:
        user (ForeignKey): Referencia al modelo Member, con eliminación en cascada.
        notifications (ManyToManyField): Relación con el modelo 'posts.Category', con nombre relacionado 'notificaciones' y opcional.
        additional_notifications (JSONField): Campo JSON para notificaciones adicionales, con valor por defecto una lista vacía.
        receive (BooleanField): Indica si el usuario desea recibir notificaciones, por defecto True.
    Métodos:
        __str__(): Retorna una cadena representativa de las notificaciones del usuario.
        get_additional_notifications(): Retorna una lista de notificaciones adicionales basadas en los permisos del usuario.
    """
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    notifications = models.ManyToManyField('posts.Category', related_name='notificaciones', blank=True)
    additional_notifications = models.JSONField(default=list)
    receive = models.BooleanField(default=True)

    def __str__(self):
        """
        Devuelve una representación en cadena de la instancia del modelo.

        Returns:
            str: Una cadena que representa las notificaciones del usuario.
        """
        return f'Notificaciones de {self.user.username}'

    def get_additional_notifications(self):
        """
        Obtiene una lista de notificaciones adicionales basadas en los permisos del usuario.
        Returns:
            list: Una lista de cadenas que representan notificaciones adicionales.
        """
        additional_notifications = [
            'Informar sobre inicio de sesión',
            'Informar sobre actualización de permisos',
            'Informar sobre activación/inactivación de cuenta'
        ]

        permissions_list = [
            'posts.add_post',
            'posts.change_post',
            'posts.can_publish',
            'posts.delete_post'
        ]
        if any(self.user.has_perm(perm) for perm in permissions_list):
            additional_notifications.append('Informar sobre cambios de estado de articulos')

        return additional_notifications