from django.test import TestCase, RequestFactory, Client
from members.models import Member
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.module_loading import import_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.text import slugify
from django.utils import lorem_ipsum
from .models import *
from .forms import *
from .views import *
from .forms import ToEditPostBodyForm
from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import Http404

#################################### Pruebas unitarias para modelos ########################################
class CategoryModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            description="Test Description",
            alias="TC",
            price=10.00,
            kind="public"
        )

    def test_category_creation(self):
        # Verificar que el nombre de la categoría sea el esperado
        self.assertEqual(self.category.name, "Test Category")
        # Verificar que la descripción de la categoría sea la esperada
        self.assertEqual(self.category.description, "Test Description")
        # Verificar que el alias de la categoría sea el esperado
        self.assertEqual(self.category.alias, "TC")
        # Verificar que el precio de la categoría sea el esperado
        self.assertEqual(self.category.price, 10.00)
        # Verificar que el tipo de la categoría sea el esperado
        self.assertEqual(self.category.kind, "public")

    def test_category_str(self):
        # Verificar que la representación en cadena de la categoría sea la esperada
        self.assertEqual(str(self.category), "Test Category (public)")

    def test_category_get_absolute_url(self):
        # Verificar que la URL absoluta de la categoría sea la esperada
        expected_url = reverse('category', args=[self.category.pk, slugify(self.category.name)])
        self.assertEqual(self.category.get_absolute_url(), expected_url)

    def test_default_values(self):
        # Crear una categoría con valores por defecto y verificar cada uno
        category = Category.objects.create(name="Default Category")
        # Verificar que la descripción por defecto sea generada por lorem_ipsum
        self.assertEqual(category.description, lorem_ipsum.words(10))
        # Verificar que el alias por defecto sea una cadena vacía
        self.assertEqual(category.alias, '')
        # Verificar que el precio por defecto sea 0.00
        self.assertEqual(category.price, 0.00)
        # Verificar que el tipo por defecto sea 'free'
        self.assertEqual(category.kind, 'free')

class PostModelTest(TestCase):

    def setUp(self):
        self.member = Member.objects.create(username="testuser", password="password")
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title="Test Post",
            title_tag="Test Tag",
            summary="Test Summary",
            body="Test Body",
            author=self.member,
            status="draft",
            category=self.category,
            keywords="test, post"
        )

    def test_post_creation(self):
        # Verificar que el título del post sea el esperado
        self.assertEqual(self.post.title, "Test Post")
        # Verificar que el tag del título sea el esperado
        self.assertEqual(self.post.title_tag, "Test Tag")
        # Verificar que el resumen del post sea el esperado
        self.assertEqual(self.post.summary, "Test Summary")
        # Verificar que el cuerpo del post sea el esperado
        self.assertEqual(self.post.body, "Test Body")
        # Verificar que el autor del post sea el miembro creado
        self.assertEqual(self.post.author, self.member)
        # Verificar que el estado del post sea 'draft'
        self.assertEqual(self.post.status, "draft")
        # Verificar que la categoría del post sea la categoría creada
        self.assertEqual(self.post.category, self.category)
        # Verificar que las palabras clave del post sean las esperadas
        self.assertEqual(self.post.keywords, "test, post")

    def test_post_str(self):
        # Verificar que la representación en cadena del post sea "Título | Autor"
        self.assertEqual(str(self.post), "Test Post | testuser")

    def test_default_values(self):
        # Crear un post con valores por defecto y verificar cada uno
        post = Post.objects.create(
            title="Default Post",
            title_tag="Default Tag",
            summary="Default Summary",
            body="Default Body",
            author=self.member,
            category=self.category
        )
        # Verificar que el estado por defecto sea 'draft'
        self.assertEqual(post.status, 'draft')
        # Verificar que las palabras clave por defecto sean una cadena vacía (si son None)
        self.assertEqual(post.keywords or '', '')  # Manejar el caso de None

    def test_permissions(self):
        # Verificar que el modelo Post tiene el permiso personalizado 'can_publish'
        self.assertIn(('can_publish', 'Can publish post'), Post._meta.permissions)

class ReportModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description',
            alias='TC',
            price=0.00,
            kind='free',
            moderated=True
        )
        self.member = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.post = Post.objects.create(
            title='Test Post',
            title_tag='Test Post Tag',
            summary='Test Summary',
            body='Test Body',
            author=self.member,
            status='draft',
            category=self.category,
            date_posted=timezone.now()
        )

    def test_report_creation(self):
        report = Report.objects.create(
            post=self.post,
            user=self.member,
            email='testuser@example.com',
            reason='Test Reason'
        )
        self.assertEqual(report.post, self.post)
        self.assertEqual(report.user, self.member)
        self.assertEqual(report.email, 'testuser@example.com')
        self.assertEqual(report.reason, 'Test Reason')
        self.assertIsNotNone(report.timestamp)

    def test_unique_constraint(self):
        Report.objects.create(
            post=self.post,
            email='testuser@example.com',
            reason='Test Reason'
        )
        with self.assertRaises(ValidationError):
            report = Report(
                post=self.post,
                email='testuser@example.com',
                reason='Another Reason'
            )
            report.full_clean()  

    def test_str_representation(self):
        report = Report.objects.create(
            post=self.post,
            user=self.member,
            email='testuser@example.com',
            reason='Test Reason'
        )
        self.assertEqual(str(report), f'Reporte por {self.member} a {self.post}')
#################################### Pruebas unitarias para formularios ########################################
class CategoryFormTest(TestCase):

    def test_valid_form(self):
        data = {
            'name': 'Test Category',
            'alias': 'te',  # Ensure alias meets validation requirements
            'description': 'A test category description',
            'kind': 'public',  # Ensure 'standard' is a valid option in the form
            'price': 0
        }
        form = CategoryForm(data=data)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_valid_form_with_price_for_premium(self):
        data = {
            'name': 'Test Category',
            'alias': 'te',  # Ensure alias meets validation requirements
            'description': 'A test category description',
            'kind': 'premium',  # Ensure 'premium' is a valid option in the form
            'price': 100
        }
        form = CategoryForm(data=data)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

class CategoryEditFormTest(TestCase):

    def setUp(self):
        self.category_data = {
            'name': 'Test Category',
            'alias': 'te',
            'description': 'A test category',
            'kind': 'public',
            'price': None
        }

    def test_valid_form(self):
        form = CategoryEditForm(data=self.category_data)
        self.assertTrue(form.is_valid())

    def test_missing_price_for_premium_category(self):
        self.category_data['kind'] = 'premium'
        form = CategoryEditForm(data=self.category_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        self.assertEqual(form.errors['price'], ['El precio es requerido para categorias premium.'])

    def test_non_premium_category_without_price(self):
        self.category_data['kind'] = 'public'
        form = CategoryEditForm(data=self.category_data)
        self.assertTrue(form.is_valid())

class MyPostEditGeneralFormTests(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            title_tag='Test Tag',
            summary='Test Summary',
            body='Test Body',
            author=self.user,
            category=self.category,
            status='draft'
        )
        self.form_data = {
            'title': 'Updated Test Post',
            'title_tag': 'Updated Test Tag',
            'summary': 'Updated Test Summary',
            'category': self.category.id,
            'status': 'to_edit',
            'keywords': 'test, post, updated'
        }

    def test_form_valid(self):
        form = MyPostEditGeneralForm(data=self.form_data, instance=self.post)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")

    def test_form_invalid(self):
        invalid_data = self.form_data.copy()
        invalid_data['title'] = ''  # Title is required
        form = MyPostEditGeneralForm(data=invalid_data, instance=self.post)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si falta el título")
        self.assertIn('title', form.errors, "El formulario debería contener errores para el campo 'title'")

    def test_form_save(self):
        form = MyPostEditGeneralForm(data=self.form_data, instance=self.post)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")
        updated_post = form.save()
        self.assertEqual(updated_post.title, 'Updated Test Post', "El título del post debería actualizarse correctamente")
        self.assertEqual(updated_post.title_tag, 'Updated Test Tag', "La etiqueta del título del post debería actualizarse correctamente")
        self.assertEqual(updated_post.summary, 'Updated Test Summary', "El resumen del post debería actualizarse correctamente")
        self.assertEqual(updated_post.category, self.category, "La categoría del post debería actualizarse correctamente")
        self.assertEqual(updated_post.status, 'to_edit', "El estado del post debería actualizarse correctamente")
        self.assertEqual(updated_post.keywords, 'test, post, updated', "Las palabras clave del post deberían actualizarse correctamente")

class MyPostEditThumbnailFormTests(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            title_tag='Test Tag',
            summary='Test Summary',
            body='Test Body',
            author=self.user,
            category=self.category,
            status='draft'
        )
        self.form_data = {
            'thumbnail': SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        }

    def test_form_initialization_with_thumbnail(self):
        self.post.thumbnail = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        self.post.save()
        form = MyPostEditThumbnailForm(instance=self.post)
        self.assertIn('data-current-url', form.fields['thumbnail'].widget.attrs)
        self.assertEqual(form.fields['thumbnail'].widget.attrs['data-current-url'], self.post.thumbnail.url)

    def test_form_initialization_without_thumbnail(self):
        form = MyPostEditThumbnailForm(instance=self.post)
        self.assertIn('data-current-url', form.fields['thumbnail'].widget.attrs)
        self.assertEqual(form.fields['thumbnail'].widget.attrs['data-current-url'], '')

    def test_form_invalid(self):
        invalid_data = {'thumbnail': SimpleUploadedFile(name='test_image.txt', content=b'', content_type='text/plain')}
        form = MyPostEditThumbnailForm(data={}, files=invalid_data, instance=self.post)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si el archivo no es una imagen")

class MyPostEditProgramFormTests(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            title_tag='Test Tag',
            summary='Test Summary',
            body='Test Body',
            author=self.user,
            category=self.category,
            status='draft'
        )
        self.form_data = {
            'publish_start_date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'publish_end_date': (timezone.now() + timezone.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        }

    def test_form_initialization_with_dates(self):
        self.post.publish_start_date = timezone.now()
        self.post.publish_end_date = timezone.now() + timezone.timedelta(days=1)
        self.post.save()
        form = MyPostEditProgramForm(instance=self.post)
        self.assertEqual(form.fields['publish_start_date'].initial, self.post.publish_start_date.strftime('%Y-%m-%dT%H:%M'))
        self.assertEqual(form.fields['publish_end_date'].initial, self.post.publish_end_date.strftime('%Y-%m-%dT%H:%M'))

    def test_form_initialization_without_dates(self):
        form = MyPostEditProgramForm(instance=self.post)
        self.assertIsNone(form.fields['publish_start_date'].initial)
        self.assertIsNone(form.fields['publish_end_date'].initial)

    def test_form_valid(self):
        form = MyPostEditProgramForm(data=self.form_data, instance=self.post)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")

    def test_form_invalid(self):
        invalid_data = self.form_data.copy()
        invalid_data['publish_end_date'] = 'invalid-date'
        form = MyPostEditProgramForm(data=invalid_data, instance=self.post)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si la fecha de fin no es válida")

    def test_form_save(self):
        form = MyPostEditProgramForm(data=self.form_data, instance=self.post)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")
        updated_post = form.save()
        self.assertEqual(updated_post.publish_start_date.strftime('%Y-%m-%dT%H:%M'), self.form_data['publish_start_date'])
        self.assertEqual(updated_post.publish_end_date.strftime('%Y-%m-%dT%H:%M'), self.form_data['publish_end_date'])

class MyPostEditBodyFormTest(TestCase):

    def setUp(self):
        self.valid_data = {
            'body': 'Test Body',
            'status': 'draft'
        }
        self.invalid_data = {
            'body': '',
            'status': ''
        }

    def test_form_initialization(self):
        form = MyPostEditBodyForm()
        self.assertIsInstance(form, MyPostEditBodyForm, "El formulario debería ser una instancia de MyPostEditBodyForm")

    def test_form_valid_data(self):
        form = MyPostEditBodyForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"El formulario debería ser válido con datos correctos. Errores: {form.errors}")

    def test_form_invalid_data(self):
        form = MyPostEditBodyForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido cuando faltan campos obligatorios")
        self.assertIn('body', form.errors, "El campo de cuerpo debería tener errores si falta")

class ToEditPostGeneralFormTests(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            title_tag='Test Tag',
            summary='Test Summary',
            body='Test Body',
            author=self.user,
            category=self.category,
            status='draft'
        )
        self.form_data = {
            'title': 'Updated Test Post',
            'title_tag': 'Updated Test Tag',
            'summary': 'Updated Test Summary',
            'category': self.category.id,
            'keywords': 'test, post, updated',
            'status': 'draft'
        }

    def test_form_initialization(self):
        form = ToEditPostGeneralForm(instance=self.post)
        self.assertIn('title', form.fields)
        self.assertIn('title_tag', form.fields)
        self.assertIn('summary', form.fields)
        self.assertIn('category', form.fields)
        self.assertIn('keywords', form.fields)
        self.assertIn('status', form.fields)
        self.assertEqual(form.fields['title'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['title'].widget.attrs['placeholder'], 'Insertar título')

    def test_form_valid(self):
        form = ToEditPostGeneralForm(data=self.form_data, instance=self.post)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")

    def test_form_invalid(self):
        invalid_data = self.form_data.copy()
        invalid_data['title'] = ''  # El título es un campo obligatorio
        form = ToEditPostGeneralForm(data=invalid_data, instance=self.post)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si el título está vacío")

    def test_form_save(self):
        form = ToEditPostGeneralForm(data=self.form_data, instance=self.post)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")
        updated_post = form.save()
        self.assertEqual(updated_post.title, 'Updated Test Post', "El título del post debería actualizarse correctamente")
        self.assertEqual(updated_post.title_tag, 'Updated Test Tag', "La etiqueta del título del post debería actualizarse correctamente")
        self.assertEqual(updated_post.summary, 'Updated Test Summary', "El resumen del post debería actualizarse correctamente")
        self.assertEqual(updated_post.keywords, 'test, post, updated', "Las palabras clave del post deberían actualizarse correctamente")

class ToEditPostBodyFormTest(TestCase):

    def setUp(self):
        self.valid_data = {
            'media': 'Valid Media',
            'body': 'Valid Body'
        }
        self.invalid_data = {
            'media': '',
            'body': ''
        }

    def test_form_initialization(self):
        form = ToEditPostBodyForm()
        self.assertIsInstance(form, ToEditPostBodyForm, "El formulario debería ser una instancia de ToEditPostBodyForm")

    def test_form_valid_data(self):
        form = ToEditPostBodyForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"El formulario debería ser válido con datos correctos. Errores: {form.errors}")

    def test_form_invalid_data(self):
        form = ToEditPostBodyForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido cuando faltan campos obligatorios")
        self.assertIn('body', form.errors, "El campo de cuerpo debería tener errores si el cuerpo falta")

    def test_form_labels(self):
        form = ToEditPostBodyForm()
        self.assertEqual(form.fields['body'].label, 'Text', "La etiqueta del cuerpo debería ser 'Text'")

class MyPostAddGeneralFormTests(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category = Category.objects.create(name='Test Category')
        self.form_data = {
            'title': 'Test Post',
            'title_tag': 'Test Tag',
            'summary': 'Test Summary',
            'category': self.category.id,
            'keywords': 'test, post'
        }

    def test_form_initialization(self):
        form = MyPostAddGeneralForm()
        self.assertIn('title', form.fields)
        self.assertIn('title_tag', form.fields)
        self.assertIn('summary', form.fields)
        self.assertIn('category', form.fields)
        self.assertIn('keywords', form.fields)
        self.assertEqual(form.fields['title'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['title'].widget.attrs['placeholder'], 'Insertar título')

    def test_form_valid(self):
        form = MyPostAddGeneralForm(data=self.form_data)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")

    def test_form_invalid(self):
        invalid_data = self.form_data.copy()
        invalid_data['title'] = ''  # El título es un campo obligatorio
        form = MyPostAddGeneralForm(data=invalid_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si el título está vacío")

    def test_form_save(self):
        form = MyPostAddGeneralForm(data=self.form_data)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")
        post = form.save(commit=False)
        post.author = self.user
        post.save()
        self.assertEqual(post.title, 'Test Post', "El título del post debería guardarse correctamente")
        self.assertEqual(post.title_tag, 'Test Tag', "La etiqueta del título del post debería guardarse correctamente")
        self.assertEqual(post.summary, 'Test Summary', "El resumen del post debería guardarse correctamente")
        self.assertEqual(post.category, self.category, "La categoría del post debería guardarse correctamente")
        self.assertEqual(post.keywords, 'test, post', "Las palabras clave del post deberían guardarse correctamente")

class MyPostAddThumbnailFormTests(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            title_tag='Test Tag',
            summary='Test Summary',
            body='Test Body',
            author=self.user,
            category=self.category,
            status='draft'
        )
        self.form_data = {
            'thumbnail': SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        }

    def test_form_initialization(self):
        form = MyPostAddThumbnailForm()
        self.assertIn('thumbnail', form.fields)
        self.assertEqual(form.fields['thumbnail'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['thumbnail'].widget.attrs['accept'], 'image/*')
        self.assertEqual(form.fields['thumbnail'].widget.attrs['data-current-url'], '')

    def test_form_invalid(self):
        invalid_data = self.form_data.copy()
        invalid_data['thumbnail'] = SimpleUploadedFile(name='test_image.txt', content=b'', content_type='text/plain')
        form = MyPostAddThumbnailForm(data={}, files=invalid_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si el archivo no es una imagen")

class MyPostAddProgramFormTests(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            title_tag='Test Tag',
            summary='Test Summary',
            body='Test Body',
            author=self.user,
            category=self.category,
            status='draft'
        )
        self.form_data = {
            'publish_start_date': timezone.now(),
            'publish_end_date': timezone.now() + timezone.timedelta(days=1)
        }

    def test_form_valid(self):
        form = MyPostAddProgramForm(data=self.form_data)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")

    def test_form_save(self):
        form = MyPostAddProgramForm(data=self.form_data, instance=self.post)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")
        post = form.save(commit=False)
        post.author = self.user
        post.save()
        self.assertEqual(post.publish_start_date, self.form_data['publish_start_date'], "La fecha de inicio de publicación debería guardarse correctamente")
        self.assertEqual(post.publish_end_date, self.form_data['publish_end_date'], "La fecha de fin de publicación debería guardarse correctamente")

class MyPostAddBodyFormTest(TestCase):

    def setUp(self):
        self.valid_data = {
            'body': 'Test Body'
        }
        self.invalid_data = {
            'body': ''
        }

    def test_form_initialization(self):
        form = MyPostAddBodyForm()
        self.assertIsInstance(form, MyPostAddBodyForm, "El formulario debería ser una instancia de MyPostAddBodyForm")

    def test_form_valid_data(self):
        form = MyPostAddBodyForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"El formulario debería ser válido con datos correctos. Errores: {form.errors}")

    def test_form_invalid_data(self):
        form = MyPostAddBodyForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido cuando faltan campos obligatorios")
        self.assertIn('body', form.errors, "El campo de cuerpo debería tener errores si falta")

class KanbanBoardFormTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name='Test Category')

    def test_kanban_board_form_valid_data(self):
        form = KanbanBoardForm(data={
            'title': 'Test Post',
            'status': 'draft',
            'author': self.user.id,
            'category': self.category.id
        })
        self.assertTrue(form.is_valid())

    def test_kanban_board_form_missing_title(self):
        form = KanbanBoardForm(data={
            'status': 'draft',
            'author': self.user.id,
            'category': self.category.id
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_kanban_board_form_missing_status(self):
        form = KanbanBoardForm(data={
            'title': 'Test Post',
            'author': self.user.id,
            'category': self.category.id
        })
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)

    def test_kanban_board_form_missing_author(self):
        form = KanbanBoardForm(data={
            'title': 'Test Post',
            'status': 'draft',
            'category': self.category.id
        })
        self.assertFalse(form.is_valid())
        self.assertIn('author', form.errors)

    def test_kanban_board_form_missing_category(self):
        form = KanbanBoardForm(data={
            'title': 'Test Post',
            'status': 'draft',
            'author': self.user.id
        })
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)

    def test_kanban_board_form_invalid_status(self):
        form = KanbanBoardForm(data={
            'title': 'Test Post',
            'status': 'invalid_status',
            'author': self.user.id,
            'category': self.category.id
        })
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)

class ToPublishPostFormTests(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            title_tag='Test Tag',
            summary='Test Summary',
            body='Test Body',
            author=self.user,
            category=self.category,
            status='draft'
        )
        self.form_data = {
            'status': 'published',
            'change_reason': 'Publishing the post'
        }

    def test_form_initialization(self):
        form = ToPublishPostForm()
        self.assertIn('status', form.fields)
        self.assertIn('change_reason', form.fields)
        self.assertEqual(form.fields['status'].widget.__class__.__name__, 'HiddenInput')
        self.assertEqual(form.fields['change_reason'].widget.__class__.__name__, 'HiddenInput')

    def test_form_valid(self):
        form = ToPublishPostForm(data=self.form_data, instance=self.post)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")

    def test_form_invalid(self):
        invalid_data = self.form_data.copy()
        invalid_data['status'] = ''  # El estado es un campo obligatorio
        form = ToPublishPostForm(data=invalid_data, instance=self.post)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si el estado está vacío")

class ReportFormTests(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            title_tag='Test Tag',
            summary='Test Summary',
            body='Test Body',
            author=self.user,
            category=self.category,
            status='published'
        )
        self.report = Report.objects.create(
            post=self.post,
            email='test@example.com',
            reason='Test Reason'
        )
        self.form_data = {
            'post': self.post.id,
            'email': 'new@example.com',
            'reason': 'New Reason'
        }

    def test_form_initialization(self):
        form = ReportForm()
        self.assertIn('post', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('reason', form.fields)

    def test_form_valid(self):
        form = ReportForm(data=self.form_data)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")

#################################### Pruebas unitarias para vistas ########################################

class CategoriesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 3 categories for testing
        Category.objects.create(name='Category 1')
        Category.objects.create(name='Category 2')
        Category.objects.create(name='Category 3')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/categories/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('categories'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('categories'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/categories.html')

    def test_context_data(self):
        response = self.client.get(reverse('categories'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('object_list' in response.context)
        self.assertEqual(len(response.context['object_list']), 3)

    def test_ordering(self):
        response = self.client.get(reverse('categories'))
        self.assertEqual(response.status_code, 200)
        categories = response.context['object_list']
        self.assertEqual(categories[0].name, 'Category 3')
        self.assertEqual(categories[1].name, 'Category 2')
        self.assertEqual(categories[2].name, 'Category 1')

class CategoryAddViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_with_permission = Member.objects.create_user(username='user_with_perm', email='user_with_perm@example.com', password='password')
        self.user_without_permission = Member.objects.create_user(username='user_without_perm', email='user_without_perm@example.com', password='password')
        permission = Permission.objects.get(codename='add_category')
        self.user_with_permission.user_permissions.add(permission)
        self.url = reverse('category_add')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_forbidden_if_no_permission(self):
        self.client.login(username='user_without_perm', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_access_for_user_with_permission(self):
        self.client.login(username='user_with_perm', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'categories/category_add.html')

    def test_invalid_form_submission(self):
        self.client.login(username='user_with_perm', password='password')
        form_data = {
            'name': '',  # Invalid data: name is required
            'description': 'A new category description'
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Category.objects.filter(description='A new category description').exists())
        self.assertContains(response, 'Este campo es obligatorio.', html=True)

class CategoryDetailViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.post1 = Post.objects.create(title='Test Post 1', category=self.category, status='published', author=self.user)
        self.post2 = Post.objects.create(title='Test Post 2', category=self.category, status='draft', author=self.user)
        self.view = CategoryDetailView()

    def test_get_object(self):
        request = self.factory.get(reverse('category', kwargs={'pk': self.category.pk, 'name': 'Test-Category'}))
        request.user = self.user
        self.view.request = request
        self.view.kwargs = {'pk': self.category.pk, 'name': 'Test-Category'}
        obj = self.view.get_object()
        self.assertEqual(obj, self.category)

    def test_get_context_data(self):
        request = self.factory.get(reverse('category', kwargs={'pk': self.category.pk, 'name': 'Test-Category'}))
        request.user = self.user
        self.view.request = request
        self.view.kwargs = {'pk': self.category.pk, 'name': 'Test-Category'}
        self.view.object = self.view.get_object()  # Ensure the object is set
        context = self.view.get_context_data()
        self.assertIn('category', context)
        self.assertEqual(context['category'], self.category)

    def test_get_object_404(self):
        request = self.factory.get(reverse('category', kwargs={'pk': 999, 'name': 'Non-Existent-Category'}))
        request.user = self.user
        self.view.request = request
        self.view.kwargs = {'pk': 999, 'name': 'Non-Existent-Category'}
        with self.assertRaises(Http404):
            self.view.get_object()

class CategoryEditViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.view = CategoryEditView()
        self.url = reverse('category_edit', kwargs={'pk': self.category.pk, 'name': 'Test-Category'})

    def test_get_object(self):
        request = self.factory.get(self.url)
        request.user = self.user
        self.view.request = request
        self.view.kwargs = {'pk': self.category.pk, 'name': 'Test-Category'}
        obj = self.view.get_object()
        self.assertEqual(obj, self.category)

    def test_get_object_not_found(self):
        request = self.factory.get(reverse('category_edit', kwargs={'pk': 999, 'name': 'Non-Existent-Category'}))
        request.user = self.user
        self.view.request = request
        self.view.kwargs = {'pk': 999, 'name': 'Non-Existent-Category'}
        with self.assertRaises(Http404):
            self.view.get_object()

    def test_permission_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

        self.client.login(username='testuser', password='12345')
        self.user.user_permissions.remove(Permission.objects.get(codename='change_category'))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # Forbidden

class CategoryDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_with_permission = self.create_user_with_permission()
        self.user_without_permission = self.create_user_without_permission()
        self.category = Category.objects.create(name="Test Category")
        self.delete_url = reverse('category_delete', kwargs={'pk': self.category.pk, 'name': self.category.name.replace(' ', '-')})

    def create_user_with_permission(self):
        user = Member.objects.create_user(username='user_with_perm', email='user_with_perm@example.com', password='password')
        permission = Permission.objects.get(codename='delete_category')
        user.user_permissions.add(permission)
        return user

    def create_user_without_permission(self):
        return Member.objects.create_user(username='user_without_perm', email='user_without_perm@example.com', password='password')

    def test_permission_denied(self):
        self.client.login(username='user_without_perm', password='password')
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)

    def test_redirection_after_deletion(self):
        self.client.login(username='user_with_perm', password='password')
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse('categories'))

    def test_successful_deletion(self):
        self.client.login(username='user_with_perm', password='password')
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())

class MyPostsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name="Test Category")
        self.post1 = Post.objects.create(title='Test Post 1', category=self.category, status='published', author=self.user, date_posted=timezone.now())
        self.post2 = Post.objects.create(title='Test Post 2', category=self.category, status='published', author=self.user, date_posted=timezone.now() - timezone.timedelta(days=1))

    def test_view_requires_login(self):
        response = self.client.get(reverse('my-posts'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_view_requires_permission(self):
        self.client.login(username='testuser', password='12345')
        self.user.user_permissions.remove(Permission.objects.get(codename='add_post'))
        response = self.client.get(reverse('my-posts'))
        self.assertEqual(response.status_code, 200)  # Forbidden

class MyPostEditViewTest(TestCase):
    def setUp(self):
        # Create the author and another user
        self.author = Member.objects.create_user(username='author', email='author@example.com', password='password')
        self.other_user = Member.objects.create_user(username='otheruser', email='other@example.com', password='password')

        # Create a category and a post by the author
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title='Original Title',
            title_tag='Original Tag',
            summary='Original Summary',
            body='Original Body',
            category=self.category,
            author=self.author
        )

    def test_other_user_cannot_access_edit_view(self):
        self.client.login(username='otheruser', password='password')
        response = self.client.get(reverse('edit-my-post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 403)

class MyPostDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_with_permission = self.create_user_with_permission()
        self.user_without_permission = Member.objects.create_user(username='user_without_perm', email='user_without_perm@example.com', password='password')
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(title='Test Post', category=self.category, status='published', author=self.user_with_permission, date_posted=timezone.now())
        self.delete_url = reverse('delete-my-post', args=[self.post.pk])

    def create_user_with_permission(self):
        user = Member.objects.create_user(username='user_with_perm', email='user_with_perm@example.com', password='password')
        user.user_permissions.add(Permission.objects.get(codename='delete_post'))
        return user

    def test_non_existent_post(self):
        non_existent_url = reverse('delete-my-post', args=[999])
        response = self.client.post(non_existent_url)
        self.assertEqual(response.status_code, 302)

    def test_permission_denied(self):
        self.client.login(username='user_without_perm', password='password')
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 405)

class MyPostAddViewTest(TestCase):
    def setUp(self):
        self.user = Member.objects.create_user(username='testuser', password='12345', email='testuser@example.com', first_name='Test', last_name='User')
        self.user.user_permissions.add(Permission.objects.get(codename='add_post'))
        self.client.login(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.valid_data_info = {
            'title': 'Test Title',
            'title_tag': 'Test Title Tag',
            'summary': 'Test Summary',
            'category': self.category.id,
            'keywords': 'test, post'
        }
        self.valid_data_body = {
            'body': 'Test Body'
        }
        self.invalid_data_info = {
            'title': '',
            'title_tag': '',
            'summary': '',
            'category': '',
            'keywords': ''
        }
        self.invalid_data_body = {
            'body': ''
        }

    def test_get_add_post_view(self):
        response = self.client.get(reverse('add-my-post'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create/create.html')

    def test_post_add_post_view_valid_data(self):
        response = self.client.post(reverse('add-my-post'), data={**self.valid_data_info, **self.valid_data_body})
        self.assertEqual(response.status_code, 302)  # Redirect after successful post creation
        self.assertTrue(Post.objects.filter(title='Test Title').exists())

    def test_post_add_post_view_invalid_data(self):
        response = self.client.post(reverse('add-my-post'), data={**self.invalid_data_info, **self.invalid_data_body})
        self.assertEqual(response.status_code, 200)  # Form re-rendered with errors
        self.assertFalse(Post.objects.filter(title='').exists())

class ToEditViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_with_permission = Member.objects.create_user(username='editor', email='editor@example.com', password='password')
        self.user_without_permission = Member.objects.create_user(username='no_perm', email='no_perm@example.com', password='password')
        self.category = Category.objects.create(name='Test Category')
        self.post1 = Post.objects.create(title='Test Post 1', category=self.category, status='to_edit', author=self.user_with_permission, date_posted=timezone.now())
        self.post2 = Post.objects.create(title='Test Post 2', category=self.category, status='to_edit', author=self.user_with_permission, date_posted=timezone.now() - timezone.timedelta(days=1))
        self.url = reverse('to-edit')

    def test_view_with_permission(self):
        self.client.login(username='editor', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_without_permission(self):
        self.client.login(username='no_perm', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

class ToEditPostViewTest(TestCase):
    def setUp(self):
        # Create the author and another user
        self.author = Member.objects.create_user(username='author', email='author@example.com', password='password')
        self.other_user = Member.objects.create_user(username='otheruser', email='other@example.com', password='password')

        # Assign the 'change_post' permission to the other user
        self.change_post_permission = Permission.objects.get(codename='change_post')
        self.other_user.user_permissions.add(self.change_post_permission)

        # Create a category and a post by the author
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title='Original Title',
            title_tag='Original Tag',
            summary='Original Summary',
            body='Original Body',
            category=self.category,
            author=self.author
        )

    def test_author_cannot_access_other_edit_view(self):
        self.client.login(username='author', password='password')
        response = self.client.get(reverse('edit-my-post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)

    def test_other_user_without_permission_cannot_access_edit_view(self):
        self.other_user.user_permissions.remove(self.change_post_permission)
        self.client.login(username='otheruser', password='password')
        response = self.client.get(reverse('edit-my-post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 403)

class ToPublishViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        permission = Permission.objects.get(codename='can_publish')
        self.user.user_permissions.add(permission)
        self.category = Category.objects.create(name='Test Category')
        self.post1 = Post.objects.create(title='Test Post 1', category=self.category, status='to_publish', author=self.user, date_posted=timezone.now())
        self.post2 = Post.objects.create(title='Test Post 2', category=self.category, status='to_publish', author=self.user, date_posted=timezone.now() - timezone.timedelta(days=1))
        self.url = reverse('to-publish')

    def test_permission_required(self):
        self.client.login(username='testuser', password='12345')
        self.user.user_permissions.remove(Permission.objects.get(codename='can_publish'))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

class ToPublishPostViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        permission = Permission.objects.get(codename='can_publish')
        self.user.user_permissions.add(permission)
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(title='Test Post', category=self.category, status='to_publish', author=self.user, date_posted=timezone.now())
        self.url = reverse('publish-a-post', args=[self.post.pk])

    def test_invalid_post_id(self):
        self.client.login(username='testuser', password='12345')
        invalid_url = reverse('publish-a-post', args=[9999])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 200)

    def test_post_status_update_to_edit(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(self.url, {'status': 'to_edit'})
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, 'to_edit')

    def test_post_status_update_to_published(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(self.url, {'status': 'published'})
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, 'published')

class SuscriberExplorePostsViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')
        self.post1 = Post.objects.create(
            title='Post 1',
            title_tag='Tag 1',
            summary='Summary 1',
            body='Body 1',
            author=self.user,
            category=self.category1,
            status='published',
            publish_start_date=timezone.now() - timezone.timedelta(days=1),
            publish_end_date=timezone.now() + timezone.timedelta(days=1)
        )
        self.post2 = Post.objects.create(
            title='Post 2',
            title_tag='Tag 2',
            summary='Summary 2',
            body='Body 2',
            author=self.user,
            category=self.category2,
            status='published',
            publish_start_date=None,
            publish_end_date=None
        )

    def test_view_response(self):
        request = self.factory.get(reverse('posts'))
        request.user = self.user
        response = SuscriberExplorePostsView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_queryset_filtering(self):
        request = self.factory.get(reverse('posts'))
        request.user = self.user
        view = SuscriberExplorePostsView()
        view.request = request
        queryset = view.get_queryset()
        self.assertIn(self.post1, queryset)
        self.assertIn(self.post2, queryset)

class SuscriberFeedPostsViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')
        self.post1 = Post.objects.create(
            title='Post 1',
            title_tag='Tag 1',
            summary='Summary 1',
            body='Body 1',
            author=self.user,
            category=self.category1,
            status='published',
            publish_start_date=timezone.now() - timezone.timedelta(days=1),
            publish_end_date=timezone.now() + timezone.timedelta(days=1)
        )
        self.post2 = Post.objects.create(
            title='Post 2',
            title_tag='Tag 2',
            summary='Summary 2',
            body='Body 2',
            author=self.user,
            category=self.category2,
            status='published',
            publish_start_date=None,
            publish_end_date=None
        )
        self.user.purchased_categories.add(self.category1)
        self.user.suscribed_categories.add(self.category2)

    def test_view_response(self):
        request = self.factory.get(reverse('feed'))
        request.user = self.user
        response = SuscriberFeedPostsView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_queryset_filtering(self):
        request = self.factory.get(reverse('feed'))
        request.user = self.user
        view = SuscriberFeedPostsView()
        view.request = request
        queryset = view.get_queryset()
        self.assertIn(self.post1, queryset)
        self.assertIn(self.post2, queryset)

class SearchExplorePostViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')
        self.post1 = Post.objects.create(
            title='Post 1',
            title_tag='Tag 1',
            summary='Summary 1',
            body='Body 1',
            author=self.user,
            category=self.category1,
            status='published',
            publish_start_date=timezone.now() - timezone.timedelta(days=1),
            publish_end_date=timezone.now() + timezone.timedelta(days=1)
        )
        self.post2 = Post.objects.create(
            title='Post 2',
            title_tag='Tag 2',
            summary='Summary 2',
            body='Body 2',
            author=self.user,
            category=self.category2,
            status='published',
            publish_start_date=None,
            publish_end_date=None
        )

    def test_view_response(self):
        request = self.factory.get(reverse('post_search_explore'))
        request.user = self.user
        response = SearchExplorePostView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_queryset_filtering_with_query(self):
        request = self.factory.get(reverse('post_search_explore'), {'q': 'Post 1'})
        request.user = self.user
        view = SearchExplorePostView()
        view.request = request
        queryset = view.get_queryset()
        self.assertIn(self.post1, queryset)
        self.assertNotIn(self.post2, queryset)

    def test_queryset_filtering_without_query(self):
        request = self.factory.get(reverse('post_search_explore'))
        request.user = self.user
        view = SearchExplorePostView()
        view.request = request
        queryset = view.get_queryset()
        self.assertIn(self.post1, queryset)
        self.assertIn(self.post2, queryset)

class SearchFeedPostViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')
        self.user.purchased_categories.add(self.category1)

        self.post1 = Post.objects.create(
            title='Post 1',
            author=self.user,
            status='published',
            category=self.category1,
            publish_start_date=timezone.now() - timezone.timedelta(days=1),
            publish_end_date=timezone.now() + timezone.timedelta(days=1),
            priority=1
        )
        self.post2 = Post.objects.create(
            title='Post 2',
            author=self.user,
            status='published',
            category=self.category2,
            publish_start_date=timezone.now() - timezone.timedelta(days=1),
            publish_end_date=timezone.now() + timezone.timedelta(days=1),
            priority=2
        )

    def test_get_queryset_without_search_query(self):
        request = self.factory.get(reverse('post_search_feed'))
        request.user = self.user
        response = SearchFeedPostView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post1, response.context_data['post_search'])
        self.assertNotIn(self.post2, response.context_data['post_search'])

    def test_get_queryset_with_search_query(self):
        request = self.factory.get(reverse('post_search_feed'), {'q': 'Post 1'})
        request.user = self.user
        response = SearchFeedPostView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post1, response.context_data['post_search'])
        self.assertNotIn(self.post2, response.context_data['post_search'])

    def test_get_context_data(self):
        request = self.factory.get(reverse('post_search_feed'))
        request.user = self.user
        response = SearchFeedPostView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('categories', response.context_data)
        self.assertEqual(list(response.context_data['categories']), list(Category.objects.all()))

class SuscriberPostDetailViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category_public = Category.objects.create(name='Public Category', kind='public')
        self.category_private = Category.objects.create(name='Private Category', kind='premium')
        self.post_public = Post.objects.create(
            title='Public Post',
            author=self.user,
            category=self.category_public,
            status='published',
            date_posted=timezone.now()
        )
        self.post_private = Post.objects.create(
            title='Private Post',
            author=self.user,
            category=self.category_private,
            status='published',
            date_posted=timezone.now()
        )

    def test_get_object_valid(self):
        view = SuscriberPostDetailView()
        view.kwargs = {'pk': self.post_public.pk, 'category': 'public-category', 'month': self.post_public.date_posted.strftime('%m'), 'year': self.post_public.date_posted.strftime('%Y'), 'title': 'public-post'}
        obj = view.get_object()
        self.assertEqual(obj, self.post_public)

class KanbanBoardViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Member.objects.create_user(username='testuser', password='12345', email='testuser@example.com')
        self.user_with_perms = Member.objects.create_user(username='testuser_with_perms', password='12345', email='testuser_with_perms@example.com')
        self.user_with_perms.user_permissions.add(Permission.objects.get(codename='add_post'))
        self.user_with_perms.user_permissions.add(Permission.objects.get(codename='change_post'))
        self.user_with_perms.user_permissions.add(Permission.objects.get(codename='can_publish'))

        self.draft_post = Post.objects.create(title='Draft Post', status='draft', author=self.user)
        self.to_edit_post = Post.objects.create(title='To Edit Post', status='to_edit', author=self.user)
        self.to_publish_post = Post.objects.create(title='To Publish Post', status='to_publish', author=self.user)
        self.published_post = Post.objects.create(title='Published Post', status='published', author=self.user)

    def tearDown(self):
        self.user.delete()
        self.user_with_perms.delete()
        Post.objects.all().delete()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('kanban-board'))
        self.assertRedirects(response, '/accounts/login/?next=/posts/kanban-board/')

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get('/kanban-board/')
        self.assertEqual(response.status_code, 200)

    def test_view_accessible_by_name(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('kanban-board'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('kanban-board'))
        self.assertTemplateUsed(response, 'kanban/kanban_board.html')

    def test_context_data_for_user_with_permissions(self):
        self.client.login(username='testuser_with_perms', password='12345')
        response = self.client.get(reverse('kanban-board'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('draft_posts', response.context)
        self.assertIn('to_edit_posts', response.context)
        self.assertIn('to_publish_posts', response.context)
        self.assertIn('published_posts', response.context)
        self.assertEqual(list(response.context['draft_posts']), [self.draft_post])
        self.assertEqual(list(response.context['to_edit_posts']), [self.to_edit_post])
        self.assertEqual(list(response.context['to_publish_posts']), [self.to_publish_post])
        self.assertEqual(list(response.context['published_posts']), [self.published_post])

    def test_context_data_for_user_without_permissions(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('kanban-board'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('draft_posts', response.context)
        self.assertIn('to_edit_posts', response.context)
        self.assertIn('to_publish_posts', response.context)
        self.assertIn('published_posts', response.context)
        self.assertEqual(list(response.context['draft_posts']), [self.draft_post])
        self.assertEqual(list(response.context['to_edit_posts']), [self.to_edit_post])
        self.assertEqual(list(response.context['to_publish_posts']), [self.to_publish_post])
        self.assertEqual(list(response.context['published_posts']), [self.published_post])

    def test_post_request_with_invalid_form(self):
        self.client.login(username='testuser_with_perms', password='12345')
        form_data = {'title': '', 'status': 'draft', 'author': self.user_with_perms.id}
        response = self.client.post(reverse('kanban-board'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kanban/kanban_board.html')
        self.assertFalse(response.context['form'].is_valid())

class UpdatePostsStatusViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Member.objects.create_user(username='testuser', password='12345', email='testuser@example.com')
        self.client.login(username='testuser', password='12345')

    def test_empty_movedPosts_list(self):
        response = self.client.post(reverse('update-posts-status'), data={'movedPosts': []}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})

    def test_invalid_json_data(self):
        response = self.client.post(reverse('update-posts-status'), data='invalid json', content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_post_does_not_exist(self):
        response = self.client.post(reverse('update-posts-status'), data={'movedPosts': [{'id': 9999, 'status': 'published'}]}, content_type='application/json')
        self.assertEqual(response.status_code, 200)

class HistoryViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Member.objects.create_user(username='testuser', password='12345', email='testuser@example.com')
        self.post = Post.objects.create(title="Test Post", body="Test Body", author=self.user)
        self.history_instance = self.post.history.first()

    def test_get_context_data(self):
        # Test if the context data contains the correct post and post_pk
        view = HistoryView()
        view.kwargs = {'pk': self.post.pk, 'history_id': self.history_instance.history_id}
        view.object = view.get_object()
        context = view.get_context_data()
        self.assertEqual(context['post'], self.history_instance)
        self.assertEqual(context['post_pk'], self.post.pk)

class RelevantPostsViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.category = Category.objects.create(name='Test Category')
        self.post1 = Post.objects.create(
            title='Post 1',
            title_tag='Tag 1',
            summary='Summary 1',
            body='Body 1',
            author=self.user,
            category=self.category,
            status='published',
            publish_start_date=timezone.now() - timezone.timedelta(days=1),
            publish_end_date=timezone.now() + timezone.timedelta(days=1),
            priority=1
        )
        self.post2 = Post.objects.create(
            title='Post 2',
            title_tag='Tag 2',
            summary='Summary 2',
            body='Body 2',
            author=self.user,
            category=self.category,
            status='published',
            publish_start_date=None,
            publish_end_date=None,
            priority=2
        )

    def test_view_response(self):
        request = self.factory.get(reverse('relevant-posts'))
        request.user = self.user
        response = RelevantPostsView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_queryset_filtering(self):
        request = self.factory.get(reverse('relevant-posts'))
        request.user = self.user
        view = RelevantPostsView()
        view.request = request
        queryset = view.get_queryset()
        self.assertIn(self.post1, queryset)
        self.assertIn(self.post2, queryset)


class ReportPostViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.client = Client()
        self.client.login(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            title_tag='Test Tag',
            summary='Test Summary',
            body='Test Body',
            author=self.user,
            status='draft',
            category=self.category,
            keywords='test, post',
            date_posted=timezone.now()  # Ensure date_posted is set
        )
        self.url_kwargs = {
            'pk': self.post.id,
            'category': slugify(self.category.name),
            'month': self.post.date_posted.strftime('%m'),
            'year': self.post.date_posted.strftime('%Y'),
            'title': slugify(self.post.title)
        }

    def test_get_request(self):
        request = self.factory.get(reverse('report_post', kwargs=self.url_kwargs))
        request.user = self.user
        self._add_middleware(request)
        response = ReportPostView.as_view()(request, **self.url_kwargs)
        self.assertEqual(response.status_code, 200)

    def _add_middleware(self, request):
        middleware = [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]
        for mw in middleware:
            mw_instance = import_string(mw)(lambda req: None)
            mw_instance.process_request(request)
        request._messages = FallbackStorage(request)

class TogglePostStatusViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.user.user_permissions.add(Permission.objects.get(codename='change_post'))
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(
            title='Test Post',
            author=self.user,
            category=self.category,
            date_posted=timezone.now() - timedelta(days=1),
            status='inactive'
        )
        self.url = reverse('toggle_post_status', args=[self.post.pk])

    def test_toggle_post_status(self):
        request = self.factory.post(self.url)
        request.user = self.user

        # Simulate necessary middlewares
        middleware = [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]
        for mw in middleware:
            mw_instance = import_string(mw)(lambda req: None)
            mw_instance.process_request(request)
        request._messages = FallbackStorage(request)

        response = TogglePostStatusView.as_view()(request, pk=self.post.pk)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('incidents'))

        # Refresh the post from the database
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, 'published')

        # Toggle back to inactive
        response = TogglePostStatusView.as_view()(request, pk=self.post.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('incidents'))

        # Refresh the post from the database
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, 'inactive')

class SubscribeViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.user.user_permissions.add(Permission.objects.get(codename='view_post'))
        self.category = Category.objects.create(name='Test Category', kind='free')
        self.premium_category = Category.objects.create(name='Premium Category', kind='premium', price=10.00)
        self.url = reverse('subscribe', kwargs={'category_id': self.category.id})
        self.premium_url = reverse('subscribe', kwargs={'category_id': self.premium_category.id})

    def test_subscribe_to_non_premium_category(self):
        request = self.factory.post(self.url)
        request.user = self.user

        # Simulate necessary middlewares
        middleware = [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]
        for mw in middleware:
            mw_instance = import_string(mw)(lambda req: None)
            mw_instance.process_request(request)
        request._messages = FallbackStorage(request)

        response = SubscribeView.as_view()(request, category_id=self.category.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('category', kwargs={'pk': self.category.pk, 'name': self.category.name}))
        self.assertIn(self.category, self.user.suscribed_categories.all())

    def test_subscribe_to_premium_category(self):
        request = self.factory.post(self.premium_url)
        request.user = self.user

        # Simulate necessary middlewares
        middleware = [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]
        for mw in middleware:
            mw_instance = import_string(mw)(lambda req: None)
            mw_instance.process_request(request)
        request._messages = FallbackStorage(request)

        response = SubscribeView.as_view()(request, category_id=self.premium_category.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('category', kwargs={'pk': self.premium_category.pk, 'name': self.premium_category.name}))

class UnsubscribeViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name='Test Category', kind='free')
        self.user.suscribed_categories.add(self.category)
        self.url = reverse('unsubscribe', kwargs={'category_id': self.category.id})

    def test_unsubscribe_from_category(self):
        request = self.factory.post(self.url)
        request.user = self.user

        # Simulate necessary middlewares
        middleware = [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]
        for mw in middleware:
            mw_instance = import_string(mw)(lambda req: None)
            mw_instance.process_request(request)
        request._messages = FallbackStorage(request)

        response = UnsubscribeView.as_view()(request, category_id=self.category.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('category', kwargs={'pk': self.category.pk, 'name': self.category.name}))
        self.assertNotIn(self.category, self.user.suscribed_categories.all())

    def test_unsubscribe_from_non_subscribed_category(self):
        new_category = Category.objects.create(name='New Category', kind='free')
        url = reverse('unsubscribe', kwargs={'category_id': new_category.id})
        request = self.factory.post(url)
        request.user = self.user

        # Simulate necessary middlewares
        middleware = [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]
        for mw in middleware:
            mw_instance = import_string(mw)(lambda req: None)
            mw_instance.process_request(request)
        request._messages = FallbackStorage(request)

        response = UnsubscribeView.as_view()(request, category_id=new_category.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('category', kwargs={'pk': new_category.pk, 'name': new_category.name}))
        self.assertNotIn(new_category, self.user.suscribed_categories.all())

class MyCategoriesViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category1 = Category.objects.create(name='Category 1', kind='free')
        self.category2 = Category.objects.create(name='Category 2', kind='premium')
        self.category3 = Category.objects.create(name='Category 3', kind='free')
        self.user.suscribed_categories.add(self.category1)
        self.user.purchased_categories.add(self.category2)
        self.url = reverse('my_categories')

    def test_view_my_categories(self):
        request = self.factory.get(self.url)
        request.user = self.user

        response = MyCategoriesView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.category1, response.context_data['suscribed_categories'])
        self.assertIn(self.category2, response.context_data['suscribed_categories'])
        self.assertNotIn(self.category3, response.context_data['suscribed_categories'])