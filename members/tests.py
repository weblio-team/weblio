from django.test import TestCase
from .models import Member
from members.forms import MemberCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from members.forms import PasswordChangingForm

class MemberModelTests(TestCase):

    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'is_active': True,
            'is_staff': False,
        }

    def test_create_member(self):
        # Test de creación de un miembro con datos válidos
        member = Member.objects.create_user(**self.user_data)
        self.assertEqual(member.username, self.user_data['username'], "El nombre de usuario no coincide")
        self.assertEqual(member.first_name, self.user_data['first_name'], "El nombre no coincide")
        self.assertEqual(member.last_name, self.user_data['last_name'], "El apellido no coincide")
        self.assertEqual(member.email, self.user_data['email'], "El correo electrónico no coincide")
        self.assertTrue(member.is_active, "El miembro debería estar activo por defecto")
        self.assertFalse(member.is_staff, "El miembro no debería ser parte del staff por defecto")

    def test_create_member_missing_fields(self):
        # Test de creación de un miembro con campos obligatorios faltantes
        with self.assertRaises(TypeError, msg="La creación de un miembro sin campos obligatorios debería lanzar TypeError"):
            Member.objects.create_user(username='testuser')

    def test_str_method(self):
        # Test del método __str__
        member = Member.objects.create_user(**self.user_data)
        self.assertEqual(str(member), member.username, "El método __str__ debería retornar el nombre de usuario")

    def test_default_permissions(self):
        # Test de permisos por defecto
        member = Member.objects.create_user(**self.user_data)
        self.assertFalse(member.is_superuser, "Un nuevo miembro no debería ser superusuario por defecto")
        self.assertFalse(member.is_staff, "Un nuevo miembro no debería ser parte del staff por defecto")

    def test_custom_manager_methods(self):
        member = Member.objects.create_user(**self.user_data)
        self.assertIsNotNone(Member.objects.get(username='testuser'), "El miembro debería existir en la base de datos")

class MemberCreationFormTest(TestCase):

    def setUp(self):
        self.valid_data = {
            'email': 'weblio@weblio.com',
            'password1': 'cincoenIS2',
            'password2': 'cincoenIS2'
        }
        self.invalid_data = {
            'email': '',
            'password1': 'password123',
            'password2': 'password123'
        }

    def test_form_initialization(self):
        form = MemberCreationForm()
        self.assertIsInstance(form, MemberCreationForm, "El formulario debería ser una instancia de MemberCreationForm")

    def test_form_valid_data(self):
        form = MemberCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"El formulario debería ser válido con datos correctos. Errores: {form.errors}")

    def test_form_invalid_data(self):
        form = MemberCreationForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido cuando faltan campos obligatorios")
        self.assertIn('email', form.errors, "El campo de correo electrónico debería tener errores si el email falta")

    def test_form_labels(self):
        form = MemberCreationForm()
        self.assertEqual(form.fields['email'].label, 'Correo electrónico', "La etiqueta del correo electrónico debería ser 'Correo electrónico'")

class PasswordChangingFormTest(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(username='testuser', password='old_password')
        self.form_data = {
            'old_password': 'old_password',
            'new_password1': 'new_password123',
            'new_password2': 'new_password123'
        }

    def test_form_initialization(self):
        form = PasswordChangingForm(user=self.user)
        self.assertIsInstance(form, PasswordChangeForm)
        self.assertFalse(form.is_bound)

    def test_form_initialization_with_data(self):
        form = PasswordChangingForm(user=self.user, data=self.form_data)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())

    def test_form_validation_with_valid_data(self):
        form = PasswordChangingForm(user=self.user, data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_validation_with_invalid_data(self):
        invalid_data = self.form_data.copy()
        invalid_data['new_password2'] = 'different_password'
        form = PasswordChangingForm(user=self.user, data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)

    def test_form_fields_labels(self):
        form = PasswordChangingForm(user=self.user)
        self.assertEqual(form.fields['old_password'].label, 'Contraseña actual')
        self.assertEqual(form.fields['new_password1'].label, 'Nueva contraseña')
        self.assertEqual(form.fields['new_password2'].label, 'Confirmar nueva contraseña')

    def test_form_fields_widget_attributes(self):
        form = PasswordChangingForm(user=self.user)
        self.assertEqual(form.fields['old_password'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['new_password1'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['new_password2'].widget.attrs['class'], 'form-control')