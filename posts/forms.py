from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from .models import Category, Post, Post
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.safestring import mark_safe

# forms for categories views
class CategoryForm(forms.ModelForm):
    """
    Formulario para crear y editar categorías.

    Este formulario permite crear y editar categorías solicitando un nombre, alias,
    descripción, tipo y precio. Valida que el precio sea requerido para categorías premium.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo, los campos, las etiquetas y los widgets del formulario.

    Métodos:
    --------
    clean():
        Valida que el precio sea requerido para categorías premium.
    """
    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        labels : dict
            Etiquetas personalizadas para los campos del formulario.
        widgets : dict
            Widgets personalizados para los campos del formulario.
        """
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
        """
        Valida que el precio sea requerido para categorías premium.

        Si el tipo de categoría es 'premium' y no se ha proporcionado un precio,
        añade un error al campo 'price'.

        Returns:
        --------
        dict
            Los datos limpiados del formulario.
        """
        cleaned_data = super().clean()
        kind = cleaned_data.get('kind')
        price = cleaned_data.get('price')

        if kind == 'premium' and not price:
            self.add_error('price', 'El precio es requerido para categorias premium.')

        return cleaned_data

class CategoryEditForm(forms.ModelForm):
    """
    Formulario para editar categorías.

    Este formulario permite editar categorías solicitando un nombre, alias,
    descripción, tipo y precio. Valida que el precio sea requerido para categorías premium.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo, los campos, las etiquetas y los widgets del formulario.

    Métodos:
    --------
    clean():
        Valida que el precio sea requerido para categorías premium.
    """
    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        labels : dict
            Etiquetas personalizadas para los campos del formulario.
        widgets : dict
            Widgets personalizados para los campos del formulario.
        """
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
        """
        Valida que el precio sea requerido para categorías premium.

        Si el tipo de categoría es 'premium' y no se ha proporcionado un precio,
        añade un error al campo 'price'.

        Returns:
        --------
        dict
            Los datos limpiados del formulario.
        """
        cleaned_data = super().clean()
        kind = cleaned_data.get('kind')
        price = cleaned_data.get('price')

        if kind == 'premium' and not price:
            self.add_error('price', 'El precio es requerido para categorias premium.')

        return cleaned_data
    
# forms for authors views
class MyPostEditInformationForm(forms.ModelForm):
    """
    Formulario para editar la información de una publicación.

    Este formulario permite editar la información de una publicación solicitando un título,
    etiqueta del título, resumen, cuerpo, categoría, estado, etiquetas, miniatura y fechas de publicación.
    Utiliza widgets personalizados para cada campo.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo, los campos, las etiquetas y los widgets del formulario.
    """
    change_reason = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        labels : dict
            Etiquetas personalizadas para los campos del formulario.
        widgets : dict
            Widgets personalizados para los campos del formulario.
        """
        model = Post
        fields = ['title', 'title_tag', 'summary', 'category', 'status', 'keywords', 'thumbnail', 'publish_start_date', 'publish_end_date']
        labels = {
            'title': _('Título'),
            'title_tag': _('Etiqueta del Título'),
            'summary': _('Resumen'),
            'category': _('Categoría'),
            'author': _('Autor'),
            'status': _('Estado'),
            'keywords': _('Etiquetas'),
            'thumbnail': _('Miniatura'),
            'publish_start_date': _('Fecha de inicio de vigencia'),
            'publish_end_date': _('Fecha de fin de vigencia'),
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar título'}),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiqueta de título'}),
            'summary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar resumen'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiquetas'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'publish_start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Insertar fecha de inicio de vigencia'}),
            'publish_end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Insertar fecha de fin de vigencia'}),
            'status': forms.HiddenInput(),
        }


class MyPostEditBodyForm(forms.ModelForm):
    """
    Formulario para editar el cuerpo de una publicación.

    Este formulario permite editar el cuerpo de una publicación utilizando un widget de CKEditor.
    Valida que el campo del cuerpo no esté vacío.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo, los campos y los widgets del formulario.

    Métodos:
    --------
    clean_body():
        Valida que el campo del cuerpo no esté vacío.
    """
    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        widgets : dict
            Widgets personalizados para los campos del formulario.
        """
        model = Post
        fields = ['body']
        widgets = {
            'body': CKEditorUploadingWidget(attrs={"class": "ckeditor", 'required': True}),
        }

    def clean_body(self):
        """
        Valida que el campo del cuerpo no esté vacío.

        Si el campo del cuerpo está vacío, lanza una excepción de validación.

        Returns:
        --------
        str
            El contenido del cuerpo validado.

        Raises:
        -------
        forms.ValidationError
            Si el campo del cuerpo está vacío.
        """
        body = self.cleaned_data.get('body')
        if not body:
            raise forms.ValidationError("Este campo es obligatorio.")
        return body
        

class ToEditPostInformationForm(forms.ModelForm):
    """
    Formulario para editar la información de una publicación.

    Este formulario permite editar la información de una publicación solicitando un título,
    etiqueta del título, resumen, categoría, etiquetas y estado. Utiliza widgets personalizados
    para cada campo.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo, los campos y los widgets del formulario.
    """
    change_reason = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        widgets : dict
            Widgets personalizados para los campos del formulario.
        """
        model = Post
        fields = ['title', 'title_tag', 'summary', 'category', 'keywords', 'status']
        widgets = {
                'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar título'}),
                'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiqueta de título'}),
                'summary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar resumen'}),
                'category': forms.Select(attrs={'class': 'form-control'}),
                'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiquetas'}),
                'status': forms.HiddenInput(),
        }

class ToEditPostBodyForm(forms.ModelForm):
    """
    Formulario para editar el cuerpo de una publicación.

    Este formulario permite editar el cuerpo de una publicación utilizando un widget de CKEditor.
    Valida que el campo del cuerpo sea obligatorio.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo, los campos y los widgets del formulario.

    Métodos:
    --------
    __init__(*args, **kwargs):
        Inicializa el formulario y establece el campo 'body' como obligatorio.
    """
    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        widgets : dict
            Widgets personalizados para los campos del formulario.
        """
        model = Post
        fields = ['body']
        widgets = {
            'body': CKEditorUploadingWidget(attrs={"class": "ckeditor", 'required': True}),
        }
    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y establece el campo 'body' como obligatorio.

        Parameters:
        -----------
        *args : list
            Argumentos posicionales.
        **kwargs : dict
            Argumentos de palabras clave.
        """
        super().__init__(*args, **kwargs)
        self.fields['body'].required = True


class MyPostAddInformationForm(forms.ModelForm):
    """
    Formulario para agregar información de una publicación.

    Este formulario permite agregar información de una publicación solicitando un título,
    etiqueta del título, resumen, categoría y etiquetas. Utiliza widgets personalizados
    para cada campo.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo, los campos y los widgets del formulario.
    """
    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        widgets : dict
            Widgets personalizados para los campos del formulario.
        """
        model = Post
        fields = ['title', 'title_tag', 'summary', 'category', 'keywords']  # Include the relevant fields

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar título'}),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiqueta de título'}),
            'summary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar resumen'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiquetas'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'publish_start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'publish_end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class MyPostAddBodyForm(forms.ModelForm):
    """
    Formulario para agregar el cuerpo de una publicación.

    Este formulario permite agregar el cuerpo de una publicación utilizando un widget de Textarea.
    Valida que el campo del cuerpo sea obligatorio.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo, los campos y los widgets del formulario.

    Métodos:
    --------
    clean_body():
        Valida que el campo del cuerpo no esté vacío.
    """
    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        widgets : dict
            Widgets personalizados para los campos del formulario.
        """
        model = Post
        fields = ['body']  # Include body, media, and status fields

        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Insertar cuerpo'}),
        }

    def clean_body(self):
        """
        Valida que el campo del cuerpo no esté vacío.

        Si el campo del cuerpo está vacío, lanza una excepción de validación.

        Returns:
        --------
        str
            El contenido del cuerpo validado.

        Raises:
        -------
        forms.ValidationError
            Si el campo del cuerpo está vacío.
        """
        body = self.cleaned_data.get('body')
        if not body:
            raise forms.ValidationError("Este campo es obligatorio.")
        return body
    

class KanbanBoardForm(forms.ModelForm):
    """
    Formulario para el tablero Kanban.

    Este formulario permite crear y editar publicaciones en un tablero Kanban solicitando un título,
    estado, autor y categoría.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo y los campos del formulario.
    """
    class Meta:
        """
        Metadatos del formulario.

        Atributos:
        ----------
        model : Model
            El modelo que se utilizará para el formulario.
        fields : list
            Lista de campos que se incluirán en el formulario.
        """
        model = Post
        fields = ['title', 'status', 'author', 'category']

class ToPublishPostForm(forms.ModelForm):
    change_reason = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Post
        fields = ['status']
        widgets = {
            'status': forms.HiddenInput(),
        }