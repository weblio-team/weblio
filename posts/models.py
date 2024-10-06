from django.db import models
from django.utils import lorem_ipsum
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from members.models import Member
from ckeditor_uploader.fields import RichTextUploadingField
from members.models import Member
import requests
from simple_history.models import HistoricalRecords
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site
from django.conf import settings
from django.apps import apps

# Create your models here.
class Category(models.Model):
    """
    Representa una categoría que agrupa diferentes publicaciones.

    Atributos:
    ----------
    name : str
        Nombre de la categoría.
    description : str
        Descripción corta de la categoría.
    alias : str
        Alias o abreviatura de la categoría.
    price : Decimal
        Precio asociado a la categoría, con un valor mínimo de 0.00.
    kind : str
        Tipo de categoría, puede ser 'public', 'free' o 'premium'.
    moderated : bool
        Indica si la categoría está moderada.

    Métodos:
    --------
    __str__():
        Retorna una representación legible de la categoría, incluyendo su nombre y tipo.
    get_absolute_url():
        Devuelve la URL canónica para una instancia específica de la categoría.
    """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, default=lorem_ipsum.words(10))
    alias = models.CharField(max_length=2, default='')
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)], null=True, blank=True)
    kind = models.CharField(max_length=20, choices=(('public', 'Public'), ('free', 'Free'), ('premium', 'Premium'),), default='free')
    moderated = models.BooleanField(default=True)

    def __str__(self):
        """Retorna el nombre de la categoría junto con su tipo."""
        return f"{self.name} ({self.kind})" + (" (No moderada)" if not self.moderated else "")
    
    def get_absolute_url(self):
        """
        Devuelve la URL canónica para la categoría.

        Returns:
            str: URL para acceder a la categoría.
        """
        return reverse('category', args=[
            self.pk,
            slugify(self.name)])

def get_default_category():
    """
    Obtiene o crea la categoría por defecto 'Uncategorized'.

    Returns:
    --------
    int
        ID de la categoría por defecto.
    """
    return Category.objects.get_or_create(name='Uncategorized')[0].id

def get_lorem_ipsum_text():
    """
    Obtiene texto de ejemplo de la API de Loripsum.

    Returns:
    --------
    str
        Texto de ejemplo obtenido de la API.
    """
    response = requests.get('https://loripsum.net/api/15/long/headers/decorate/link/ul/ol/dl/bq/code')
    if response.status_code == 200:
        return response.text
    return ''

class Post(models.Model):
    """
    Representa una publicación o artículo que pertenece a una categoría.

    Atributos:
    ----------
    title : str
        Título del post.
    title_tag : str
        Etiqueta del título para SEO.
    summary : str
        Resumen breve del post.
    body : str
        Contenido principal del post, que soporta texto enriquecido.
    date_posted : datetime
        Fecha y hora en que se creó el post.
    author : Member
        Autor del post, relacionado con un usuario.
    status : str
        Estado actual del post ('draft', 'to_edit', 'to_publish', 'published').
    category : Category
        Categoría a la que pertenece el post.
    keywords : str
        Palabras clave asociadas al post para SEO.
    thumbnail : ImageField
        Miniatura de la publicación.
    publish_start_date : datetime
        Fecha de inicio de publicación.
    publish_end_date : datetime
        Fecha de fin de publicación.
    change_reason : str
        Razón del cambio.
    priority : int
        Prioridad del post.
    
    Métodos:
    --------
    __str__():
        Retorna una representación legible del post, incluyendo el título y el autor.
    get_absolute_url():
        Devuelve la URL canónica para una instancia específica del post.
    calculate_priority():
        Calcula la prioridad del post basado en el tipo de categoría (kind).
    save(*args, **kwargs):
        Sobrescribe el método save para establecer date_posted cuando el estado cambia a 'published'.
    send_status_change_email(old_status):
        Envía un correo electrónico notificando el cambio de estado del post.
    get_status_display(status_value):
        Traduce el valor del estado a una versión legible (en español).

    Meta:
    -----
    permissions : list
        Lista de permisos personalizados para el modelo.
    """

    title = models.CharField(max_length=100)
    title_tag = models.CharField(max_length=100)
    summary = models.CharField(max_length=100, default=lorem_ipsum.words(10)) 
    body = RichTextUploadingField('Text', blank=True, default=get_lorem_ipsum_text)
    date_posted = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    author = models.ForeignKey(Member, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=(('draft', 'Draft'), ('to_edit', 'To Edit'), ('to_publish', 'To Publish'), ('published', 'Published'), ('inactive', 'Inactive')), default='draft')
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=get_default_category)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    history = HistoricalRecords()
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    publish_start_date = models.DateTimeField(blank=True, null=True)
    publish_end_date = models.DateTimeField(blank=True, null=True)
    change_reason = models.CharField(max_length=255, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)

    class Meta:
        permissions = [
            ('can_publish', 'Can publish post'),
        ]

    def __str__(self):
        """Retorna el título del post junto con el nombre del autor."""
        return self.title + ' | ' + str(self.author)
    
    def get_absolute_url(self):
        """
        Devuelve la URL canónica para el post.

        Returns:
            str: URL para acceder al post.
        """
        return reverse('post', args=[
            self.pk,
            slugify(self.category.name),
            self.date_posted.strftime('%m'),
            self.date_posted.strftime('%Y'),
            slugify(self.title)
        ])
    
    def calculate_priority(self):
        """
        Calcula la prioridad del post basado en el tipo de categoría (kind).

        1: public
        2: free
        3: premium
        """
        if self.category.kind == 'public':
            return 1
        elif self.category.kind == 'free':
            return 2
        elif self.category.kind == 'premium':
            return 3
        return None
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para establecer date_posted cuando el estado cambia a 'published'.
        """
        # Establecer la fecha de publicación si el estado es 'published' y la fecha de publicación es nula
        if self.status == 'published' and self.date_posted is None:
            self.date_posted = timezone.now()
        
        # Verificar si el status ha cambiado
        old_status = None
        if self.pk:
            old_post = Post.objects.get(pk=self.pk)
            old_status = old_post.status

        # Calcular la prioridad antes de guardar
        self.priority = self.calculate_priority() if self.priority != 4 else self.priority

        super().save(*args, **kwargs)

        # Enviar correo si el estado ha cambiado
        if old_status != self.status:
            self.send_status_change_email(old_status)

    def send_status_change_email(self, old_status):
        """
        Envía un correo electrónico notificando el cambio de estado del post.

        Args:
        -----
        old_status : str
            Estado anterior del post.

        Returns:
        --------
        None
        """
        # Recuperar el último historial
        last_history = self.history.order_by('-history_date').first()
        changed_by = last_history.history_user
        change_reason = self.change_reason or "Sin razón proporcionada"
        change_date = last_history.history_date

        # Crear la URL absoluta del post
        current_site = Site.objects.get_current()

        # Ajusta el dominio y el protocolo del sitio según la configuración
        current_site.domain = settings.SITE_DOMAIN
        site_protocol = settings.SITE_PROTOCOL


        # Obtener el estado anterior y el nuevo estado con traducción
        old_status_translated = self.get_status_display(old_status)
        new_status_translated = self.get_status_display(self.status)

        # Preparar el contexto para el correo
        context = {
            'post': self,
            'old_status': old_status_translated,
            'new_status': new_status_translated,
            'changed_by': changed_by,
            'change_reason': change_reason,
            'change_date': change_date,
        }

        # Obtener el modelo de usuario personalizado
        User = apps.get_model(settings.AUTH_USER_MODEL)

        # Obtener la lista de usuarios a notificar
        users_to_notify = set()

        # Autor del post
        if self.author.has_perm('posts.create_post'):
            author_notification = self.author.notification_set.first()
            if author_notification and 'Informar sobre cambios de estado de articulos' in author_notification.additional_notifications:
                users_to_notify.add((self.author, 'author'))

        # Editores si el estado es to_edit
        if self.status == 'to_edit':
            editors = User.objects.all()
            for editor in editors:
                if editor.has_perm('posts.change_post'):
                    editor_notification = editor.notification_set.first()
                    if editor_notification and 'Informar sobre cambios de estado de articulos' in editor_notification.additional_notifications:
                        users_to_notify.add((editor, 'editor'))

        # Publicadores si el estado es to_publish
        if self.status == 'to_publish':
            publishers = User.objects.all()
            for publisher in publishers:
                if publisher.has_perm('posts.can_publish'):
                    publisher_notification = publisher.notification_set.first()
                    if publisher_notification and 'Informar sobre cambios de estado de articulos' in publisher_notification.additional_notifications:
                        users_to_notify.add((publisher, 'publisher'))

        # Suscriptores si el estado es published
        if self.status == 'published':
            suscribers = User.objects.all()
            for user in suscribers:
                if user.has_perm('posts.view_post'):
                    if self.category in user.purchased_categories.all() or self.category in user.suscribed_categories.all():
                        users_to_notify.add((user, 'suscriber'))

        # Enviar el correo a cada usuario en la lista
        for user, user_type in users_to_notify:
            if user_type == 'author':
                subject = f"Cambio de estado de tu artículo: {self.title}"
                template = 'emails/post-status/status_change_author.html'
                post_url = f"{site_protocol}://{current_site.domain}/my-posts/{self.pk}/"
            elif user_type == 'editor':
                subject = f"Nuevo artículo pendiente de edición: {self.title}"
                template = 'emails/post-status/status_change_editor.html'
                post_url = f"{site_protocol}://{current_site.domain}/to-edit/{self.pk}/"
            elif user_type == 'publisher':
                subject = f"Nuevo artículo pendiente de publicación: {self.title}"
                template = 'emails/post-status/status_change_publisher.html'
                post_url = f"{site_protocol}://{current_site.domain}/to-publish/{self.pk}/"
            elif user_type == 'suscriber':
                subject = f"Nuevo post disponible en tus categorías de interés: {self.title}"
                template = 'emails/post-status/status_change_suscriber.html'
                post_url = f"{site_protocol}://{current_site.domain}/{self.get_absolute_url()}"
                context['user'] = user

            context['post_url'] = post_url

            from_email = settings.EMAIL_HOST_USER
            html_content = render_to_string(template, context)
            to_email = user.email
            msg = EmailMultiAlternatives(subject, '', from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

    def get_status_display(self, status_value):
        """
        Traduce el valor del estado a una versión legible (en español).

        Args:
        -----
        status_value : str
            Valor del estado.

        Returns:
        --------
        str
            Estado traducido.
        """
        status_dict = {
            'draft': 'Borrador',
            'to_edit': 'Edición',
            'to_publish': 'Publicar',
            'published': 'Publicado'
        }
        return status_dict.get(status_value, 'Desconocido')
    
class Report(models.Model):
    """
    Representa un reporte de una publicación.

    Atributos:
    ----------
    post : ForeignKey
        Publicación que está siendo reportada.
    user : ForeignKey
        Usuario que realiza el reporte (opcional).
    email : EmailField
        Correo electrónico del usuario que realiza el reporte (opcional).
    reason : TextField
        Razón del reporte.
    timestamp : DateTimeField
        Fecha y hora en que se creó el reporte.

    Métodos:
    --------
    __str__():
        Retorna una representación legible del reporte, incluyendo el usuario o correo electrónico y la publicación.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    reason = models.TextField(default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'email')

    def __str__(self):
        """
        Retorna una representación legible del reporte, incluyendo el usuario o correo electrónico y la publicación.

        Returns:
        --------
        str
            Representación legible del reporte.
        """
        return f'Reporte por {self.user or self.email} a {self.post}'