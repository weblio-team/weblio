from django.db import models
from django.utils import lorem_ipsum
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from members.models import Member
from django_ckeditor_5.fields import CKEditor5Field
from members.models import Member
import requests

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, default=lorem_ipsum.words(10))
    alias = models.CharField(max_length=2, default='')
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)], null=True, blank=True)
    kind = models.CharField(max_length=20, choices=(('public', 'Public'), ('free', 'Free'), ('premium', 'Premium'),), default='free')

    def __str__(self):
        return f"{self.name} ({self.kind})"
    
    def get_absolute_url(self):
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
    title = models.CharField(max_length=100)
    title_tag = models.CharField(max_length=100)
    summary = models.CharField(max_length=100, default=lorem_ipsum.words(10)) 
    body = CKEditor5Field('Text', config_name='extends', blank=True, default=get_lorem_ipsum_text)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Member, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=(('draft', 'Draft'), ('to_edit', 'To Edit'), ('to_publish', 'To Publish'),('published', 'Published'),), default='draft')
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=get_default_category)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        permissions = [
            ('can_publish', 'Can publish post'),
        ]

    def __str__(self):
        return self.title + ' | ' + str(self.author)
    
    def get_absolute_url(self):
        return reverse('post', args=[
            self.pk,
            slugify(self.category.name),
            self.date_posted.strftime('%m'),
            self.date_posted.strftime('%Y'),
            slugify(self.title)
        ])