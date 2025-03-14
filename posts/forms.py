from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from .models import Category, Post, Report
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
        fields = ['name', 'alias', 'description', 'kind', 'price', 'moderated']
        labels = {
            'name': _('Nombre'),
            'alias': _('Alias'),
            'description': _('Descripción'),
            'kind': _('Tipo'),
            'price': _('Precio'),
            'moderated': _('Moderado'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introduzca la categoria'}),
            'alias': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introduzca el alias'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Introduzca la descripcion', 'rows': 3}),
            'kind': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Introduzca el precio', 'id': 'id_price', 'readonly': 'readonly'}),
            'moderated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
        fields = ['name', 'alias', 'description', 'kind', 'price', 'moderated']
        labels = {
            'name': _('Nombre'),
            'alias': _('Alias'),
            'description': _('Descripción'),
            'kind': _('Tipo'),
            'price': _('Precio'),
            'moderated': _('Moderado'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introduzca la categoria'}),
            'alias': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introduzca el alias'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Introduzca la descripcion'}),
            'kind': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Introduzca el precio', 'id': 'id_price', 'readonly': 'readonly'}),
            'moderated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
class MyPostEditGeneralForm(forms.ModelForm):
    """
    Formulario para editar la información de una publicación.

    Este formulario permite editar la información de una publicación solicitando un título,
    etiqueta del título, resumen, cuerpo, categoría, estado, etiquetas, miniatura y fechas de publicación.
    Utiliza widgets personalizados para cada campo.

    Atributos:
    ----------
    change_reason : CharField
        Campo oculto para almacenar la razón del cambio.
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
        fields = ['title', 'title_tag', 'summary', 'category', 'status', 'keywords']
        labels = {
            'title': _('Título'),
            'title_tag': _('Etiqueta del Título'),
            'summary': _('Resumen'),
            'category': _('Categoría'),
            'author': _('Autor'),
            'status': _('Estado'),
            'keywords': _('Etiquetas'),
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar título'}),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiqueta de título'}),
            'summary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar resumen'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Insertar etiquetas'}),
            'status': forms.HiddenInput(),
        }

class MyPostEditThumbnailForm(forms.ModelForm):
    """
    Formulario para editar la miniatura de una publicación.

    Este formulario permite editar la miniatura de una publicación solicitando una imagen.
    Utiliza un widget personalizado para el campo de la miniatura.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo, los campos y los widgets del formulario.

    Métodos:
    --------
    __init__(*args, **kwargs):
        Inicializa el formulario y añade la URL de la miniatura actual si existe.
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
        fields = ['thumbnail']
        widgets = {
            'thumbnail': forms.ClearableFileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*',  # Solo permite imágenes
                'data-current-url': '',  # Aquí puedes agregar el atributo, pero no se muestra al usuario
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y añade la URL de la miniatura actual si existe.

        Args:
        -----
        *args : list
            Argumentos posicionales.
        **kwargs : dict
            Argumentos clave.

        Returns:
        --------
        None
        """
        super(MyPostEditThumbnailForm, self).__init__(*args, **kwargs)
        # Si ya existe una imagen subida, puedes mostrar una vista previa
        if self.instance and self.instance.pk and self.instance.thumbnail:
            self.fields['thumbnail'].widget.attrs['data-current-url'] = self.instance.thumbnail.url

class MyPostEditProgramForm(forms.ModelForm):
    """
    Formulario para editar las fechas de publicación de una publicación.

    Este formulario permite editar las fechas de inicio y fin de publicación de una publicación.
    Utiliza widgets personalizados para cada campo.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo, los campos y los widgets del formulario.

    Métodos:
    --------
    __init__(*args, **kwargs):
        Inicializa el formulario y establece los valores iniciales para las fechas de publicación.
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
        fields = ['publish_start_date', 'publish_end_date']
        widgets = {
            'publish_start_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),  # Este es el formato correcto para datetime-local
            'publish_end_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),  # Formato correcto
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y establece los valores iniciales para las fechas de publicación.

        Args:
        -----
        *args : list
            Argumentos posicionales.
        **kwargs : dict
            Argumentos clave.

        Returns:
        --------
        None
        """
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.publish_start_date:
                self.fields['publish_start_date'].initial = self.instance.publish_start_date.strftime('%Y-%m-%dT%H:%M')
            if self.instance.publish_end_date:
                self.fields['publish_end_date'].initial = self.instance.publish_end_date.strftime('%Y-%m-%dT%H:%M')

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
        

class ToEditPostGeneralForm(forms.ModelForm):
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
                'category': forms.Select(attrs={'class': 'form-control', 'id': 'id_category'}),
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


class MyPostAddGeneralForm(forms.ModelForm):
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
        }

class MyPostAddThumbnailForm(forms.ModelForm):
    """
    Formulario para agregar una miniatura a una publicación.

    Este formulario permite agregar una miniatura a una publicación solicitando una imagen.
    Utiliza un widget personalizado para el campo de la miniatura.

    Atributos:
    ----------
    Meta : class
        Clase interna que define el modelo, los campos y los widgets del formulario.

    Métodos:
    --------
    __init__(*args, **kwargs):
        Inicializa el formulario y establece un valor vacío para la URL de la miniatura actual.
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
        fields = ['thumbnail']
        widgets = {
            'thumbnail': forms.ClearableFileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*',  # Solo permite imágenes
                'data-current-url': '',  # Agregamos un atributo para la URL de la imagen actual
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y establece un valor vacío para la URL de la miniatura actual.

        Args:
        -----
        *args : list
            Argumentos posicionales.
        **kwargs : dict
            Argumentos clave.

        Returns:
        --------
        None
        """
        super(MyPostAddThumbnailForm, self).__init__(*args, **kwargs)
        # No hay imagen existente, ya que es una vista de agregar
        self.fields['thumbnail'].widget.attrs['data-current-url'] = ''

class MyPostAddProgramForm(forms.ModelForm):
    """
    Formulario para agregar las fechas de publicación de una publicación.

    Este formulario permite agregar las fechas de inicio y fin de publicación de una publicación.
    Utiliza widgets personalizados para cada campo.

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
        fields = ['publish_start_date', 'publish_end_date']
        widgets = {
            'publish_start_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Insertar fecha de inicio de vigencia',
                'type': 'datetime-local'  # Asegúrate de que el tipo sea datetime-local
            }),
            'publish_end_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Insertar fecha de fin de vigencia',
                'type': 'datetime-local'  # Asegúrate de que el tipo sea datetime-local
            }),
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
    """
    Formulario para cambiar el estado de una publicación a "publicado".

    Este formulario permite cambiar el estado de una publicación a "publicado".
    Utiliza un campo oculto para almacenar la razón del cambio y un widget oculto para el campo de estado.

    Atributos:
    ----------
    change_reason : CharField
        Campo oculto para almacenar la razón del cambio.
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
        fields = ['status']
        widgets = {
            'status': forms.HiddenInput(),
        }

class ReportForm(forms.ModelForm):
    """
    Formulario para crear un reporte de una publicación.

    Este formulario permite crear un reporte de una publicación solicitando el correo electrónico
    y la razón del reporte. Valida que no exista un reporte duplicado para la misma publicación
    y correo electrónico.

    Atributos:
    ----------
    post : ModelChoiceField
        Campo oculto para seleccionar la publicación a reportar.
    Meta : class
        Clase interna que define el modelo y los campos del formulario.

    Métodos:
    --------
    clean():
        Valida que no exista un reporte duplicado para la misma publicación y correo electrónico.
    """
    post = forms.ModelChoiceField(queryset=Post.objects.all(), widget=forms.HiddenInput())
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
        model = Report
        fields = ['post', 'email', 'reason']

    def clean(self):
        """
        Valida que no exista un reporte duplicado para la misma publicación y correo electrónico.

        Si ya existe un reporte con el mismo correo electrónico para la publicación,
        añade un error al formulario.

        Returns:
        --------
        dict
            Los datos limpiados del formulario.
        """
        cleaned_data = super().clean()
        post = cleaned_data.get('post')
        email = cleaned_data.get('email')
        if Report.objects.filter(post=post, email=email).exists():
            raise forms.ValidationError('Ya existe un reporte con este correo.')
        return cleaned_data