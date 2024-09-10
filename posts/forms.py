from django import forms
from django.urls import reverse_lazy
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
class MyPostEditInformationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'title_tag', 'summary', 'category', 'keywords']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar título'}),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiqueta de título'}),
            'summary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar resumen'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiquetas'}),
        }


class MyPostEditBodyForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['body']
        widgets = {
            'body': CKEditorUploadingWidget(attrs={"class": "ckeditor", 'required': True}),
        }

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if not body:
            raise forms.ValidationError("Este campo es obligatorio.")
        return body
        

class ToEditPostInformationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'title_tag', 'summary', 'category', 'keywords']
        widgets = {
                'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar título'}),
                'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiqueta de título'}),
                'summary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar resumen'}),
                'category': forms.Select(attrs={'class': 'form-control'}),
                'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiquetas'}),
        }

class ToEditPostBodyForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['body']
        widgets = {
            'body': CKEditorUploadingWidget(attrs={"class": "ckeditor", 'required': True}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].required = True


class MyPostAddInformationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'title_tag', 'summary', 'category', 'keywords']  # Include the relevant fields

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar título'}),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiqueta de título'}),
            'summary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar resumen'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiquetas'}),
        }


class MyPostAddBodyForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['body']  # Include body, media, and status fields

        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Insertar cuerpo'}),
        }

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if not body:
            raise forms.ValidationError("Este campo es obligatorio.")
        return body
    

class KanbanBoardForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'status', 'author', 'category']