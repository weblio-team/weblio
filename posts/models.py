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

# Create your models here.
class Category(models.Model):
    """
    Representa una categoría que agrupa diferentes publicaciones.

    Atributos:
        name (str): Nombre de la categoría.
        description (str): Descripción corta de la categoría.
        alias (str): Alias o abreviatura de la categoría.
        price (Decimal): Precio asociado a la categoría, con un valor mínimo de 0.00.
        kind (str): Tipo de categoría, puede ser 'public', 'free' o 'premium'.
    
    Métodos:
        __str__: Retorna una representación legible de la categoría, incluyendo su nombre y tipo.
        get_absolute_url: Devuelve la URL canónica para una instancia específica de la categoría.
    """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, default=lorem_ipsum.words(10))
    alias = models.CharField(max_length=2, default='')
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)], null=True, blank=True)
    kind = models.CharField(max_length=20, choices=(('public', 'Public'), ('free', 'Free'), ('premium', 'Premium'),), default='free')

    def __str__(self):
        """Retorna el nombre de la categoría junto con su tipo."""
        return f"{self.name} ({self.kind})"
    
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
    return Category.objects.get_or_create(name='Uncategorized')[0].id

def get_lorem_ipsum_text():
    response = requests.get('https://loripsum.net/api/15/long/headers/decorate/link/ul/ol/dl/bq/code')
    if response.status_code == 200:
        return response.text
    return ''

class Post(models.Model):
    """
    Representa una publicación o artículo que pertenece a una categoría.

    Atributos:
        title (str): Título del post.
        title_tag (str): Etiqueta del título para SEO.
        summary (str): Resumen breve del post.
        body (str): Contenido principal del post, que soporta texto enriquecido.
        date_posted (datetime): Fecha y hora en que se creó el post.
        author (Member): Autor del post, relacionado con un usuario.
        status (str): Estado actual del post ('draft', 'to_edit', 'to_publish', 'published').
        category (Category): Categoría a la que pertenece el post.
        keywords (str): Palabras clave asociadas al post para SEO.
    
    Métodos:
        __str__: Retorna una representación legible del post, incluyendo el título y el autor.
        get_absolute_url: Devuelve la URL canónica para una instancia específica del post.
    
    Meta:
        permissions:
            can_publish: Permite a un usuario publicar el post.
    """

    title = models.CharField(max_length=100)
    title_tag = models.CharField(max_length=100)
    summary = models.CharField(max_length=100, default=lorem_ipsum.words(10)) 
    body = RichTextUploadingField('Text', blank=True, default=get_lorem_ipsum_text)
    date_posted = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    author = models.ForeignKey(Member, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=(('draft', 'Draft'), ('to_edit', 'To Edit'), ('to_publish', 'To Publish'), ('published', 'Published'),), default='draft')
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=get_default_category)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    history = HistoricalRecords()
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    publish_start_date = models.DateTimeField(blank=True, null=True)
    publish_end_date = models.DateTimeField(blank=True, null=True)
    change_reason = models.CharField(max_length=255, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)

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
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para establecer date_posted cuando el estado cambia a 'published'.
        """
        if self.status == 'published' and self.date_posted is None:
            self.date_posted = timezone.now()
        
        # Verificar si el status ha cambiado
        old_status = None
        if self.pk:
            old_post = Post.objects.get(pk=self.pk)
            old_status = old_post.status

        super().save(*args, **kwargs)

        # Enviar correo si el estado ha cambiado
        if not settings.DEBUG and old_status != self.status:
            self.send_status_change_email(old_status)

    def send_status_change_email(self, old_status):
        # Recuperar el último historial
        last_history = self.history.order_by('-history_date').first()  # Ordenar por fecha descendente y obtener el primer registro
        changed_by = last_history.history_user
        change_reason = self.change_reason or "Sin razón proporcionada"
        change_date = last_history.history_date

        # Crear la URL absoluta del post
        current_site = Site.objects.get_current()
        post_url = f"http://{current_site.domain}/my-posts/{self.pk}/"

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
            'post_url': post_url,
        }

        # Renderizar el HTML del correo
        subject = f"Cambio de estado de tu artículo: {self.title}"
        from_email = settings.EMAIL_HOST_USER
        to_email = self.author.email
        html_content = render_to_string('emails/status_change_notification.html', context)

        # Crear y enviar el correo
        msg = EmailMultiAlternatives(subject, '', from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def get_status_display(self, status_value):
        """
        Traducir el valor del estado a una versión legible (en español).
        """
        status_dict = {
            'draft': 'Borrador',
            'to_edit': 'Edición',
            'to_publish': 'Publicar',
            'published': 'Publicado'
        }
        return status_dict.get(status_value, 'Desconocido')