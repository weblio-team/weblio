from django.db import models
from django.utils import lorem_ipsum
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator

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