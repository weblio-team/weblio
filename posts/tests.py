from django.test import TestCase, RequestFactory, Client
from members.models import Member
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from django.utils import lorem_ipsum
from .models import *
from .forms import *
from .views import *
from .forms import ToEditPostInformationForm, ToEditPostBodyForm
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


class SuscriberPostsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="TestCategory")
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.post1 = Post.objects.create(
            title="Test Post 1",
            author=self.user,
            category=self.category,
            keywords="test",
            status="published",
            date_posted=timezone.now()
        )
        self.post2 = Post.objects.create(
            title="Test Post 2",
            author=self.user,
            category=self.category,
            keywords="test",
            status="published",
            date_posted=timezone.now() - timezone.timedelta(days=1)
        )
        self.url = reverse('posts')

    def test_get_context_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('categories', context)
        self.assertEqual(list(context['categories']), list(Category.objects.all()))


class SearchPostViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name="TestCategory")
        self.post1 = Post.objects.create(
            title="Test Post 1",
            author=self.user,
            category=self.category,
            keywords="test",
            status="published",
            date_posted=timezone.now()
        )
        self.post2 = Post.objects.create(
            title="Test Post 2",
            author=self.user,
            category=self.category,
            keywords="test",
            status="published",
            date_posted=timezone.now() - timezone.timedelta(days=1)
        )
        self.url = reverse('post_search')

    def test_search_context_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('categories', context)
        self.assertEqual(list(context['categories']), list(Category.objects.all()))


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

    def test_dispatch_authenticated_user_private_post(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('post', kwargs={
            'pk': self.post_private.pk, 'category': 'private-category', 
            'month': self.post_private.date_posted.strftime('%m'), 
            'year': self.post_private.date_posted.strftime('%Y'), 
            'title': 'private-post'
        }))
        self.assertEqual(response.status_code, 200)

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