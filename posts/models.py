from django.db import models
from django.utils import lorem_ipsum
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from members.models import Member
from ckeditor_uploader.fields import RichTextUploadingField
from members.models import Member
import requests

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
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Member, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=(('draft', 'Draft'), ('to_edit', 'To Edit'), ('to_publish', 'To Publish'), ('published', 'Published'),), default='draft')
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=get_default_category)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    
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
