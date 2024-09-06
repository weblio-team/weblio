from django import forms
from django.utils.translation import gettext as _
from .models import Category, Post, Post
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.safestring import mark_safe

# forms for categories views
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'alias', 'description', 'kind', 'price']
        labels = {
            'name': _('Nombre'),
            'alias': _('Alias'),
            'description': _('Descripción'),
            'kind': _('Tipo'),
            'price': _('Precio'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introduzca la categoria'}),
            'alias': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introduzca el alias'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Introduzca la descripcion'}),
            'kind': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Introduzca el precio', 'id': 'id_price', 'readonly': 'readonly'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        kind = cleaned_data.get('kind')
        price = cleaned_data.get('price')

        if kind == 'premium' and not price:
            self.add_error('price', 'El precio es requerido para categorias premium.')

        return cleaned_data

class CategoryEditForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'alias', 'description', 'kind', 'price']
        labels = {
            'title': _('Título'),
            'title_tag': _('Etiqueta del Título'),
            'summary': _('Resumen'),
            'body': _('Cuerpo'),
            'category': _('Categoría'),
            'author': _('Autor'),
            'status': _('Estado'),
        }
        labels = {
            'name': _('Nombre'),
            'alias': _('Alias'),
            'description': _('Descripción'),
            'kind': _('Tipo'),
            'price': _('Precio'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introduzca la categoria'}),
            'alias': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introduzca el alias'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Introduzca la descripcion'}),
            'kind': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Introduzca el precio', 'id': 'id_price', 'readonly': 'readonly'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        kind = cleaned_data.get('kind')
        price = cleaned_data.get('price')

        if kind == 'premium' and not price:
            self.add_error('price', 'El precio es requerido para categorias premium.')

        return cleaned_data
    
# forms for authors views
class MyPostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'title_tag', 'summary', 'body', 'category', 'status', 'keywords']
        labels = {
            'title': _('Título'),
            'title_tag': _('Etiqueta del Título'),
            'summary': _('Resumen'),
            'body': _('Cuerpo'),
            'category': _('Categoría'),
            'author': _('Autor'),
            'status': _('Estado'),
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar título'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiqueta de título'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Insertar resumen'}),
            'body': CKEditorUploadingWidget(attrs={"class": "ckeditor"}),
            'status': forms.HiddenInput(),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiquetas'}),
        }

    def __init__(self, *args, **kwargs):
        super(MyPostEditForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.status != 'draft':
            # Eliminar el campo `body` del formulario
            self.fields.pop('body', None)

            # Deshabilitar los otros campos
            for field_name, field in self.fields.items():
                field.widget.attrs['disabled'] = 'disabled'

        
class ToEditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'title_tag', 'summary', 'body', 'category', 'author', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar titulo'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiqueta de titulo'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Insertar resumen'}),
            'body': CKEditorUploadingWidget(attrs={"class": "ckeditor"}),
            'author': forms.HiddenInput(),
            'status': forms.HiddenInput(),
        }

class MyPostAddForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'title_tag', 'summary', 'body', 'author', 'category', 'keywords']
        labels = {
            'title': _('Título'),
            'title_tag': _('Etiqueta del Título'),
            'summary': _('Resumen'),
            'body': _('Cuerpo'),
            'category': _('Categoría'),
            'author': _('Autor'),
            'status': _('Estado'),
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar titulo'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'author': forms.HiddenInput(),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiqueta de titulo'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Insertar resumen'}),
            'body': CKEditorUploadingWidget(attrs={"class": "ckeditor"}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiquetas'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(MyPostAddForm, self).__init__(*args, **kwargs)
        print(user)
        if user:
            self.fields['author'].initial = user

    def save(self, commit=True):
        instance = super(MyPostAddForm, self).save(commit=False)
        if self.initial.get('author'):
            instance.author = self.initial['author']
            print(instance.author)
        if commit:
            instance.save()
        return instance