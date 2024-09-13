from django.test import TestCase
from members.models import Member
from django.urls import reverse
from django.utils.text import slugify
from django.utils import lorem_ipsum
from .models import Category, Post
from .forms import MyPostAddInformationForm, MyPostAddBodyForm, MyPostEditInformationForm, MyPostEditBodyForm
from .forms import MyPostAddInformationForm, MyPostAddBodyForm, MyPostEditInformationForm, MyPostEditBodyForm
from .forms import ToEditPostInformationForm, ToEditPostBodyForm
from django.contrib.auth.models import Permission

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

    def test_post_get_absolute_url(self):
        # Verificar que la URL absoluta del post sea la esperada
        expected_url = reverse('post', args=[
            self.post.pk,
            slugify(self.post.category.name),
            self.post.date_posted.strftime('%m'),
            self.post.date_posted.strftime('%Y'),
            slugify(self.post.title)
        ])
        self.assertEqual(self.post.get_absolute_url(), expected_url)

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

class MyPostAddInformationFormTest(TestCase):

    def setUp(self):
        self.valid_data = {
            'title': 'Test Title',
            'title_tag': 'Test Title Tag',
            'summary': 'Test Summary',
            'category': 1,  # Assuming category with ID 1 exists
            'keywords': 'test, post'
        }
        self.invalid_data = {
            'title': '',
            'title_tag': '',
            'summary': '',
            'category': '',
            'keywords': ''
        }

    def test_form_initialization(self):
        form = MyPostAddInformationForm()
        self.assertIsInstance(form, MyPostAddInformationForm, "El formulario debería ser una instancia de MyPostAddInformationForm")

    def test_form_valid_data(self):
        form = MyPostAddInformationForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"El formulario debería ser válido con datos correctos. Errores: {form.errors}")

    def test_form_invalid_data(self):
        form = MyPostAddInformationForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido cuando faltan campos obligatorios")
        self.assertIn('title', form.errors, "El campo de título debería tener errores si falta")
        self.assertIn('category', form.errors, "El campo de categoría debería tener errores si falta")

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

class MyPostEditInformationFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'title': 'Test Title',
            'title_tag': 'Test Title Tag',
            'summary': 'Test Summary',
            'category': 1,
            'keywords': 'test, post',
            'status': 'draft'  # Añadir el campo status
        }
        self.invalid_data = {
            'title': '',
            'title_tag': '',
            'summary': '',
            'category': '',
            'keywords': '',
            'status': ''  # Añadir el campo status
        }

    def test_form_initialization(self):
        form = MyPostEditInformationForm()
        self.assertIsInstance(form, MyPostEditInformationForm, "El formulario debería ser una instancia de MyPostEditInformationForm")

    def test_form_valid_data(self):
        form = MyPostEditInformationForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"El formulario debería ser válido con datos correctos. Errores: {form.errors}")

    def test_form_invalid_data(self):
        form = MyPostEditInformationForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido cuando faltan campos obligatorios")
        self.assertIn('title', form.errors, "El campo de título debería tener errores si falta")
        self.assertIn('category', form.errors, "El campo de categoría debería tener errores si falta")
        self.assertIn('status', form.errors, "El campo de status debería tener errores si falta")

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
        """Test that a non-author cannot access the post edit view"""
        self.client.login(username='otheruser', password='password')
        response = self.client.get(reverse('edit-my-post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 403)


class ToEditPostInformationFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'title': 'Valid Title',
            'title_tag': 'Valid Tag',
            'summary': 'Valid Summary',
            'category': 1,
            'change_reason': 'Valid Reason',
            'status': 'draft'  # Añadir el campo status
        }
        self.invalid_data = {
            'title': '',
            'title_tag': '',
            'summary': '',
            'category': '',
            'change_reason': '',
            'status': ''  # Añadir el campo status
        }

    def test_form_initialization(self):
        form = ToEditPostInformationForm()
        self.assertIsInstance(form, ToEditPostInformationForm, "El formulario debería ser una instancia de ToEditPostInformationForm")

    def test_form_valid_data(self):
        form = ToEditPostInformationForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"El formulario debería ser válido con datos correctos. Errores: {form.errors}")

    def test_form_invalid_data(self):
        form = ToEditPostInformationForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido cuando faltan campos obligatorios")
        self.assertIn('title', form.errors, "El campo de título debería tener errores si el título falta")
        self.assertIn('status', form.errors, "El campo de status debería tener errores si falta")

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

    def test_other_user_without_permission_cannot_access_edit_view(self):
        """Test that a non-author without 'change_post' permission cannot access the edit view"""
        self.other_user.user_permissions.remove(self.change_post_permission)
        self.client.login(username='otheruser', password='password')
        response = self.client.get(reverse('edit-my-post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 403)