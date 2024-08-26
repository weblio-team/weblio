from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class MemberManager(BaseUserManager):
    """
    Gestor de modelo de usuario personalizado donde el email es el identificador único
    para la autenticación en lugar de los nombres de usuario.

    Hereda de:
        - BaseUserManager: Gestor base proporcionado por Django para manejar usuarios personalizados.

    Métodos:
        - create_user(email, password, **extra_fields): Crea y guarda un usuario con el email y contraseña dados.
        - create_superuser(email, password, **extra_fields): Crea y guarda un SuperUsuario con el email y contraseña dados.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Crea y guarda un usuario con el email y la contraseña proporcionados.

        Parámetros:
            - email (str): La dirección de email del usuario.
            - password (str): La contraseña para el usuario.
            - **extra_fields: Campos adicionales para el modelo de usuario.

        Retorna:
            - user: El objeto de usuario creado.

        Lanza:
            - ValueError: Si no se proporciona un email.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Crea y guarda un SuperUsuario con el email y la contraseña proporcionados.

        Parámetros:
            - email (str): La dirección de email del superusuario.
            - password (str): La contraseña para el superusuario.
            - **extra_fields: Campos adicionales para el modelo de superusuario.

        Retorna:
            - user: El objeto de superusuario creado.

        Lanza:
            - ValueError: Si los campos is_staff o is_superuser no están configurados correctamente.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)