from django.test import TestCase
from members.models import Member
from django.urls import reverse
from django.utils.text import slugify
from django.utils import lorem_ipsum
from .models import Category, Post

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