from django.test import TestCase, RequestFactory, Client
from .models import Member
from django.urls import reverse
from django.contrib.messages import get_messages
from members.forms import *
from members.views import *
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.contrib.auth.models import Group, Permission
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

#################################### Pruebas unitarias para modelos ########################################
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

class NotificationModelTests(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.notification = Notification.objects.create(user=self.user)

    def test_get_additional_notifications_with_permissions(self):
        # Add necessary permissions to the user
        permissions = [
            'add_post',
            'change_post',
            'can_publish',
            'delete_post'
        ]
        for perm in permissions:
            permission = Permission.objects.get(codename=perm)
            self.user.user_permissions.add(permission)

        expected_notifications = [
            'Informar sobre inicio de sesión',
            'Informar sobre actualización de permisos',
            'Informar sobre activación/inactivación de cuenta',
            'Informar sobre cambios de estado de articulos'
        ]
        self.assertEqual(self.notification.get_additional_notifications(), expected_notifications)

    def test_get_additional_notifications_without_permissions(self):
        expected_notifications = [
            'Informar sobre inicio de sesión',
            'Informar sobre actualización de permisos',
            'Informar sobre activación/inactivación de cuenta'
        ]
        self.assertEqual(self.notification.get_additional_notifications(), expected_notifications)

    def test_str_method(self):
        self.assertEqual(str(self.notification), f'Notificaciones de {self.user.username}')

#################################### Pruebas unitarias para formularios #####################################
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

class MemberEditFormTest(TestCase):

    def setUp(self):
        self.member = Member.objects.create(
            email='test@example.com',
            password='password123',
            is_staff=True,
            is_active=True
        )

    def test_form_valid_data(self):
        form = MemberEditForm(data={
            'email': 'newemail@example.com',
            'password': 'newpassword123',
            'is_staff': False,
            'is_active': False,
            'groups': [],
            'user_permissions': []
        }, instance=self.member)
        self.assertTrue(form.is_valid())

    def test_form_invalid_email(self):
        form = MemberEditForm(data={
            'email': 'invalid-email',
            'password': 'newpassword123',
            'is_staff': False,
            'is_active': False,
            'groups': [],
            'user_permissions': []
        }, instance=self.member)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_missing_required_fields(self):
        form = MemberEditForm(data={
            'email': '',
            'password': '',
            'is_staff': False,
            'is_active': False,
            'groups': [],
            'user_permissions': []
        }, instance=self.member)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        # Check if password is required
        if 'password' in form.fields and form.fields['password'].required:
            self.assertIn('password', form.errors)

    def test_form_initial_data(self):
        form = MemberEditForm(instance=self.member)
        self.assertEqual(form.initial['email'], 'test@example.com')
        self.assertEqual(form.initial['is_staff'], True)
        self.assertEqual(form.initial['is_active'], True)

class MemberChangeFormTest(TestCase):

    def setUp(self):
        self.member = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )

    def test_form_initialization_with_valid_data(self):
        form_data = {
            'email': 'newemail@example.com',
            'password': 'newpassword123',
            'is_staff': True,
            'is_active': True,
            'groups': [],
            'user_permissions': []
        }
        form = MemberChangeForm(instance=self.member, data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_initialization_with_missing_required_fields(self):
        form_data = {
            'email': '',
            'password': '',
            'is_staff': True,
            'is_active': True,
            'groups': [],
            'user_permissions': []
        }
        form = MemberChangeForm(instance=self.member, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        # Check if password is required
        if 'password' in form.fields and form.fields['password'].required:
            self.assertIn('password', form.errors)

    def test_email_field_validation(self):
        form_data = {
            'email': 'invalid-email',
            'password': 'newpassword123',
            'is_staff': True,
            'is_active': True,
            'groups': [],
            'user_permissions': []
        }
        form = MemberChangeForm(instance=self.member, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_field_validation(self):
        form_data = {
            'email': 'newemail@example.com',
            'password': '',
            'is_staff': True,
            'is_active': True,
            'groups': [],
            'user_permissions': []
        }
        form = MemberChangeForm(instance=self.member, data=form_data)
        self.assertTrue(form.is_valid())  # Password is not required, so form should be valid

    def test_form_errors_for_missing_required_fields(self):
        form_data = {
            'email': '',
            'password': '',
            'is_staff': True,
            'is_active': True,
            'groups': [],
            'user_permissions': []
        }
        form = MemberChangeForm(instance=self.member, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        # Check if password is required
        if 'password' in form.fields and form.fields['password'].required:
            self.assertIn('password', form.errors)

class GroupEditFormTest(TestCase):

    def setUp(self):
        self.group = Group.objects.create(name='Test Group')
        self.permission1 = Permission.objects.create(codename='perm1', name='Permission 1', content_type_id=1)
        self.permission2 = Permission.objects.create(codename='perm2', name='Permission 2', content_type_id=1)
        self.group.permissions.set([self.permission1, self.permission2])

    def test_form_valid_data(self):
        form_data = {
            'name': 'Updated Group',
            'permissions': [self.permission1.id, self.permission2.id]
        }
        form = GroupEditForm(data=form_data, instance=self.group)
        self.assertTrue(form.is_valid())

    def test_form_missing_name(self):
        form_data = {
            'permissions': [self.permission1.id, self.permission2.id]
        }
        form = GroupEditForm(data=form_data, instance=self.group)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_form_save(self):
        form_data = {
            'name': 'Updated Group',
            'permissions': [self.permission1.id, self.permission2.id]
        }
        form = GroupEditForm(data=form_data, instance=self.group)
        self.assertTrue(form.is_valid())
        group = form.save()
        self.assertEqual(group.name, 'Updated Group')
        self.assertEqual(list(group.permissions.all()), [self.permission1, self.permission2])

    def test_form_save_no_commit(self):
        form_data = {
            'name': 'Updated Group',
            'permissions': [self.permission1.id, self.permission2.id]
        }
        form = GroupEditForm(data=form_data, instance=self.group)
        self.assertTrue(form.is_valid())
        group = form.save(commit=False)
        self.assertEqual(group.name, 'Updated Group')
        group.save()
        group.permissions.set(form.cleaned_data['permissions'])
        self.assertEqual(list(group.permissions.all()), [self.permission1, self.permission2])

class UserListFormTest(TestCase):

    def setUp(self):
        self.member1 = Member.objects.create(username='user1', email='user1@example.com')
        self.member2 = Member.objects.create(username='user2', email='user2@example.com')

    def test_form_fields(self):
        form = UserListForm()
        self.assertIn('users', form.fields)
        self.assertEqual(form.fields['users'].label, "Miembros")
        self.assertTrue(form.fields['users'].required)

    def test_form_valid_data(self):
        form = UserListForm(data={'users': self.member1.id})
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        form = UserListForm(data={'users': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('users', form.errors)

class GroupListFormTest(TestCase):

    def setUp(self):
        # Create test groups
        self.group1 = Group.objects.create(name='Group 1')
        self.group2 = Group.objects.create(name='Group 2')

        # Create test permissions
        self.permission1 = Permission.objects.create(codename='perm1', name='Permission 1', content_type_id=1)
        self.permission2 = Permission.objects.create(codename='perm2', name='Permission 2', content_type_id=1)

        # Assign permissions to groups
        self.group1.permissions.add(self.permission1)
        self.group2.permissions.add(self.permission2)

    def test_form_valid_data(self):
        form_data = {
            'group': self.group1.id,
            'permissions': [self.permission1.id]
        }
        form = GroupListForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        form_data = {
            'group': '',  # Missing required field
            'permissions': [self.permission1.id]
        }
        form = GroupListForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('group', form.errors)

class CreateGroupFormTests(TestCase):

    def setUp(self):
        # Get the content type for the Member model
        member_content_type = ContentType.objects.get_for_model(Member)
        
        # Create some permissions to use in tests
        self.permission1 = Permission.objects.create(
            codename='can_add_member', 
            name='Can add member', 
            content_type=member_content_type
        )
        self.permission2 = Permission.objects.create(
            codename='can_change_member', 
            name='Can change member', 
            content_type=member_content_type
        )
        self.permission3 = Permission.objects.create(
            codename='can_delete_member', 
            name='Can delete member', 
            content_type=member_content_type
        )

    def test_form_initialization(self):
        form = CreateGroupForm()
        self.assertIn('name', form.fields)
        self.assertIn('permissions', form.fields)
        self.assertEqual(form.fields['permissions'].queryset.count(), Permission.objects.filter(
            Q(name__iregex='.*member.*') |
            Q(name__iregex='.*category.*') |
            Q(name__iregex='.*post.*') |
            Q(name__iregex='.*group.*') |
            Q(name__iregex='.*permission.*') |
            Q(name__iregex='.*publish.*')
        ).count())

    def test_form_valid_data(self):
        form_data = {
            'name': 'Test Group',
            'permissions': [self.permission1.id, self.permission2.id]
        }
        form = CreateGroupForm(data=form_data)
        self.assertTrue(form.is_valid())
        group = form.save()
        self.assertEqual(group.name, 'Test Group')
        self.assertEqual(list(group.permissions.all()), [self.permission1, self.permission2])

    def test_form_invalid_data(self):
        form_data = {
            'permissions': [self.permission1.id, self.permission2.id]
        }
        form = CreateGroupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_save_method(self):
        form_data = {
            'name': 'Test Group',
            'permissions': [self.permission1.id, self.permission2.id]
        }
        form = CreateGroupForm(data=form_data)
        self.assertTrue(form.is_valid())
        group = form.save()
        self.assertEqual(group.name, 'Test Group')
        self.assertEqual(list(group.permissions.all()), [self.permission1, self.permission2])

class MemberRegisterFormTests(TestCase):

    def setUp(self):
        # Get the content type for the Member model
        member_content_type = ContentType.objects.get_for_model(Member)
        
        # Create 'suscriptor' group for testing
        self.suscriptor_group = Group.objects.create(name='suscriptor')
        
        # Create some permissions to use in tests
        self.permission = Permission.objects.create(
            codename='can_view', 
            name='Can view', 
            content_type=member_content_type
        )
        self.suscriptor_group.permissions.add(self.permission)

    def test_form_initialization(self):
        form = MemberRegisterForm()
        self.assertIn('username', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)

    def test_password_mismatch(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password321',
        }
        form = MemberRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_valid_data(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password123',
        }
        form = MemberRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        form_data = {
            'username': '',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password123',
        }
        form = MemberRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_form_save(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password123',
        }
        form = MemberRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('password123'))
        self.assertTrue(user.is_active)
        self.assertIn(self.suscriptor_group, user.groups.all())
        self.assertIn(self.permission, user.user_permissions.all())

class MemberJoinFormTests(TestCase):

    def setUp(self):
        # Create a test group with permissions
        self.group = Group.objects.create(name='test_group')
        self.permission = Permission.objects.create(
            codename='can_view',
            name='Can view',
            content_type_id=1  # Assuming a valid content_type_id
        )
        self.group.permissions.add(self.permission)

    def test_form_initialization(self):
        form = MemberJoinForm()
        self.assertIn('username', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)
        self.assertIn('role', form.fields)

    def test_form_valid_data(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password123',
            'role': self.group.id
        }
        form = MemberJoinForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'differentpassword',
            'role': self.group.id
        }
        form = MemberJoinForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_form_save(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password123',
            'role': self.group.id
        }
        form = MemberJoinForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertFalse(user.is_active)  # User should be inactive by default
        self.assertIn(self.group, user.groups.all())
        self.assertIn(self.permission, user.user_permissions.all())

    def test_password_mismatch(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'differentpassword',
            'role': self.group.id
        }
        form = MemberJoinForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

class MemberLoginFormTests(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )

    def test_valid_form(self):
        form_data = {'username': 'testuser', 'password': 'testpassword123'}
        form = MemberLoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_username(self):
        form_data = {'password': 'testpassword123'}
        form = MemberLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_invalid_form_missing_password(self):
        form_data = {'username': 'testuser'}
        form = MemberLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

class MemberEditGroupFormTest(TestCase):

    def setUp(self):
        # Create test groups
        self.group1 = Group.objects.create(name='Group 1')
        self.group2 = Group.objects.create(name='Group 2')

        # Create a test member
        self.member = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )

    def test_form_initialization(self):
        form = MemberEditGroupForm(instance=self.member)
        self.assertIn('groups', form.fields)
        self.assertEqual(form.fields['groups'].queryset.count(), 2)

    def test_form_valid_data(self):
        form_data = {'groups': [self.group1.id, self.group2.id]}
        form = MemberEditGroupForm(data=form_data, instance=self.member)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        form_data = {'groups': ['invalid_group_id']}
        form = MemberEditGroupForm(data=form_data, instance=self.member)
        self.assertFalse(form.is_valid())

    def test_form_save(self):
        form_data = {'groups': [self.group1.id, self.group2.id]}
        form = MemberEditGroupForm(data=form_data, instance=self.member)
        self.assertTrue(form.is_valid())
        member = form.save()
        self.assertIn(self.group1, member.groups.all())
        self.assertIn(self.group2, member.groups.all())

class TestMemberEditPermissionForm(TestCase):

    def setUp(self):
        # Create test user
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        
        # Create test permissions
        self.permission1 = Permission.objects.create(codename='test_permission1', name='Test Permission 1', content_type_id=1)
        self.permission2 = Permission.objects.create(codename='test_permission2', name='Test Permission 2', content_type_id=1)
        
        # Create test group and assign permissions
        self.group = Group.objects.create(name='testgroup')
        self.group.permissions.add(self.permission1, self.permission2)
        self.user.groups.add(self.group)

    def test_form_initialization(self):
        form = MemberEditPermissionForm(instance=self.user)
        self.assertEqual(
            list(form.fields['permissions'].queryset),
            list(Permission.objects.filter(Q(group__in=self.user.groups.all())).distinct())
        )
        self.assertEqual(
            list(form.fields['permissions'].initial),
            list(self.user.user_permissions.all())
        )

    def test_form_valid_data(self):
        form_data = {'permissions': [self.permission1.id, self.permission2.id]}
        form = MemberEditPermissionForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        form_data = {'permissions': ['invalid_permission']}
        form = MemberEditPermissionForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())

class MemberStatusFormTest(TestCase):

    def setUp(self):
        self.member = Member.objects.create(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            is_active=True
        )

    def test_form_initialization(self):
        form = MemberStatusForm(instance=self.member)
        self.assertIn('is_active', form.fields)
        self.assertEqual(form.fields['is_active'].label, 'Activo')
        self.assertIsInstance(form.fields['is_active'].widget, forms.CheckboxInput)

    def test_form_valid_data(self):
        form_data = {'is_active': False}
        form = MemberStatusForm(data=form_data, instance=self.member)
        self.assertTrue(form.is_valid())
        member = form.save()
        self.assertFalse(member.is_active)

    def test_form_labels_and_widgets(self):
        form = MemberStatusForm(instance=self.member)
        self.assertEqual(form.fields['is_active'].label, 'Activo')
        self.assertIsInstance(form.fields['is_active'].widget, forms.CheckboxInput)
        self.assertEqual(form.fields['is_active'].label_suffix, '')

    def test_form_save(self):
        form_data = {'is_active': False}
        form = MemberStatusForm(data=form_data, instance=self.member)
        self.assertTrue(form.is_valid())
        member = form.save()
        self.assertFalse(member.is_active)

class MemberListFormTests(TestCase):

    def setUp(self):
        self.member1 = Member.objects.create_user(
            username='testuser1',
            first_name='Test',
            last_name='User1',
            email='testuser1@example.com',
            password='testpassword123'
        )
        self.member2 = Member.objects.create_user(
            username='testuser2',
            first_name='Test',
            last_name='User2',
            email='testuser2@example.com',
            password='testpassword123'
        )

    def test_form_initialization(self):
        form = MemberListForm()
        self.assertIn(self.member1, form.fields['users'].queryset)
        self.assertIn(self.member2, form.fields['users'].queryset)

    def test_form_valid(self):
        form_data = {'users': self.member1.id}
        form = MemberListForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form_data = {'users': ''}
        form = MemberListForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_labels(self):
        form = MemberListForm()
        self.assertEqual(form.fields['users'].label, "Miembros")

class EditProfileFormTests(TestCase):

    def setUp(self):
        self.member = Member.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            password='testpassword123'
        )

    def test_form_fields(self):
        form = EditProfileForm(instance=self.member)
        self.assertIn('email', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)

    def test_form_valid_data(self):
        form_data = {
            'email': 'newemail@example.com',
            'first_name': 'New',
            'last_name': 'Name',
            'username': 'newusername',
            'password': 'testpassword123'
        }
        form = EditProfileForm(data=form_data, instance=self.member)
        self.assertTrue(form.is_valid())

    def test_form_invalid_email(self):
        form_data = {
            'email': 'invalid-email',
            'first_name': 'New',
            'last_name': 'Name',
            'username': 'newusername',
            'password': 'testpassword123'
        }
        form = EditProfileForm(data=form_data, instance=self.member)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_empty_fields(self):
        form_data = {
            'email': '',
            'first_name': '',
            'last_name': '',
            'username': '',
            'password': ''
        }
        form = EditProfileForm(data=form_data, instance=self.member)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('username', form.errors)

class PasswordChangingFormTest(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='old_password')
        self.client.login(username='testuser', password='old_password')
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

class UserAddRoleFormTests(TestCase):

    def setUp(self):
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.group = Group.objects.create(name='Test Group')
        self.form_data = {'group': self.group.id}

    def test_form_initialization(self):
        form = UserAddRoleForm(user=self.user)
        self.assertIn('group', form.fields, "El formulario debería tener un campo 'group'")

    def test_form_valid_data(self):
        form = UserAddRoleForm(data=self.form_data, user=self.user)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con datos correctos")

    def test_form_invalid_data(self):
        form = UserAddRoleForm(data={}, user=self.user)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido cuando faltan campos obligatorios")

#################################### Pruebas unitarias para vistas ########################################
class EditProfileViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.client.login(username='testuser', password='12345')
        self.url = reverse('edit_profile')

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, "La solicitud GET debería retornar un código de estado 200")
        self.assertTemplateUsed(response, 'members/edit_profile.html', "La vista debería usar la plantilla 'edit_profile.html'")
        self.assertIsInstance(response.context['form'], EditProfileForm, "El contexto debería contener una instancia de EditProfileForm")

class UpdateProfilePictureViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.client.login(username='testuser', password='12345')
        self.url = reverse('update_profile_picture')

    def test_post_request_with_no_file(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200, "La solicitud POST debería retornar un código de estado 200")
        self.assertFalse(response.json()['success'], "La respuesta JSON debería indicar que la operación no fue exitosa")

class HomeViewTests(TestCase):
    def setUp(self):
        self.url = reverse('home')

    def test_home_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_home_view_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'home.html')

class GroupListViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')
        self.user.user_permissions.add(Permission.objects.get(codename='view_group'))
        self.group1 = Group.objects.create(name='Group1')
        self.group2 = Group.objects.create(name='Group2')
        self.permission1 = Permission.objects.create(codename='perm1', name='Permission 1', content_type_id=1)
        self.permission2 = Permission.objects.create(codename='perm2', name='Permission 2', content_type_id=1)
        self.group1.permissions.add(self.permission1)
        self.group2.permissions.add(self.permission2)

    def test_post_edit_group(self):
        request = self.factory.post(reverse('group-list'), data={'selected_group': self.group1.id, 'action': 'edit_group'})
        request.user = self.user
        response = GroupListView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('group-edit', kwargs={'pk': self.group1.id}))

    def test_post_delete_group(self):
        request = self.factory.post(reverse('group-list'), data={'selected_group': self.group1.id, 'action': 'delete_group'})
        request.user = self.user
        response = GroupListView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('group-delete', kwargs={'group_id': self.group1.id}))

class GroupEditViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.client = Client()
        self.client.login(username='testuser', password='12345')
        self.group = Group.objects.create(name='Test Group')
        self.permission1 = Permission.objects.create(
            codename='test_permission1',
            name='Test Permission 1',
            content_type_id=1
        )
        self.permission2 = Permission.objects.create(
            codename='test_permission2',
            name='Test Permission 2',
            content_type_id=1
        )
        self.url = reverse('group-edit', kwargs={'pk': self.group.pk})

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, "La solicitud GET debería retornar un código de estado 200")
        self.assertTemplateUsed(response, 'groups/group_edit.html', "La vista debería usar la plantilla 'group_edit.html'")
        self.assertIsInstance(response.context['form'], GroupEditForm, "El contexto debería contener una instancia de GroupEditForm")
        self.assertEqual(response.context['group'], self.group, "El contexto debería contener el grupo correcto")
        self.assertIn('grouped_permissions', response.context, "El contexto debería contener los permisos agrupados")
        self.assertIn('selected_permissions_ids', response.context, "El contexto debería contener los IDs de los permisos seleccionados")

    def test_post_request_valid_data(self):
        valid_data = {
            'name': 'Updated Group',
            'permissions': [self.permission2.id]
        }
        response = self.client.post(self.url, data=valid_data, follow=True)
        self.assertEqual(response.status_code, 200, "La solicitud POST debería retornar un código de estado 200")
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'Updated Group', "El nombre del grupo debería actualizarse")
        self.assertIn(self.permission2, self.group.permissions.all(), "El grupo debería tener el permiso actualizado")

    def test_post_request_invalid_data(self):
        invalid_data = {
            'name': '',
            'permissions': [self.permission2.id]
        }
        response = self.client.post(self.url, data=invalid_data, follow=True)
        self.assertEqual(response.status_code, 200, "La solicitud POST debería retornar un código de estado 200")
        self.assertFalse(response.context['form'].is_valid(), "El formulario debería ser inválido con datos incorrectos")

class GroupDeleteViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.group = Group.objects.create(name='Test Group')
        self.member1 = Member.objects.create_user(username='user1', email='user1@example.com', password='password')
        self.member2 = Member.objects.create_user(username='user2', email='user2@example.com', password='password')
        self.member1.groups.add(self.group)
        self.member2.groups.add(self.group)
        self.view = GroupDeleteView.as_view()

    def test_group_deletion_with_single_group_members(self):
        request = self.factory.get(reverse('group-delete', kwargs={'group_id': self.group.id}))
        request.user = self.member1
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, group_id=self.group.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No se puede eliminar. Existen usuarios que se quedarían sin rol.')

    def test_group_deletion_redirection_to_edit_group(self):
        request = self.factory.post(reverse('group-delete', kwargs={'group_id': self.group.id}), {'action': 'edit_group', 'selected_member': self.member1.id})
        request.user = self.member1
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, group_id=self.group.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'{reverse("member-edit-group", kwargs={"pk": self.member1.id})}?next={request.path}')

class CreateGroupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('group-create')
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.user.user_permissions.add(Permission.objects.get(codename='add_group'))
        self.user.user_permissions.add(Permission.objects.get(codename='add_permission'))
        self.client.login(username='testuser', password='testpass')

    def test_access_with_permission(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/group_create.html')

class MemberListViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.member = Member.objects.create(username='memberuser', email='member@example.com')

    def test_post_toggle_status(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('member-list'), {'selected_member': self.member.id, 'action': 'toggle_status'})

class MemberEditGroupViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.group = Group.objects.create(name='Test Group')
        self.permission = Permission.objects.get(codename='change_member')
        self.user = Member.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        self.user.user_permissions.add(self.permission)
        self.user.groups.add(self.group)
        self.user.save()

    def test_permission_denied(self):
        another_user = Member.objects.create_user(username='anotheruser', email='another@example.com', password='testpass')
        request = self.factory.get(reverse('member-edit-group', kwargs={'pk': self.user.pk}))
        request.user = another_user
        with self.assertRaises(PermissionDenied):
            MemberEditGroupView.as_view()(request, pk=self.user.pk)

class MemberEditPermissionViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.user.user_permissions.add(Permission.objects.get(codename='change_member'))
        self.user.user_permissions.add(Permission.objects.get(codename='view_member'))
        self.user.user_permissions.add(Permission.objects.get(codename='change_permission'))
        self.user.save()
        self.member = Member.objects.create(username='memberuser', email='member@example.com')
        self.permission = Permission.objects.create(
            codename='test_permission', 
            name='Test Permission', 
            content_type_id=1
        )
        self.url = reverse('member-edit-permission', kwargs={'pk': self.member.pk})
        self.view = MemberEditPermissionView.as_view()

    def test_permission_denied(self):
        self.user.user_permissions.clear()
        request = self.factory.get(self.url)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        with self.assertRaises(PermissionDenied):
            self.view(request, pk=self.member.pk)

class MemberStatusViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.group = Group.objects.create(name='test_group')
        self.admin_user = Member.objects.create_superuser(
            username='adminuser',
            email='adminuser@example.com',
            password='adminpassword'
        )
        self.member = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.member.groups.add(self.group)
        self.member.save()

        self.url = reverse('member-status', kwargs={'pk': self.member.pk})

    def test_get_member_status_view(self):
        request = self.factory.get(self.url)
        request.user = self.admin_user
        response = MemberStatusView.as_view()(request, pk=self.member.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertContains(response, 'member')

    def test_post_member_status_view_valid_data(self):
        data = {'is_active': False}
        request = self.factory.post(self.url, data)
        request.user = self.admin_user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = MemberStatusView.as_view()(request, pk=self.member.pk)
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('member-list'))

class MemberRegisterViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('member-register')
        self.valid_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        self.invalid_data = {
            'username': '',
            'email': 'invalidemail',
            'password1': 'testpassword123',
            'password2': 'differentpassword'
        }

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/member_register.html')

    def test_invalid_form_submission(self):
        response = self.client.post(self.url, data=self.invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/member_register.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertGreater(len(messages), 0)
        self.assertIn("El nombre de usuario ya está registrado.", [str(message) for message in messages])
        self.assertIn("El correo electrónico ya está registrado.", [str(message) for message in messages])

class MemberLoginViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('member-login')
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

    def test_form_valid_data(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data=form_data)
        self.assertRedirects(response, reverse('posts'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Bienvenido de vuelta testuser")

    def test_form_invalid_data(self):
        form_data = {
            'username': 'wronguser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data=form_data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Error en el nombre de usuario o contraseña. Por favor, intente de nuevo.")

class MemberJoinViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('member-join')
        self.view = MemberJoinView.as_view()
        self.group = Group.objects.create(name='test_group')

    def test_get_context_data(self):
        request = self.factory.get(self.url)
        request.user = Member.objects.create_user(username='testuser', email='test@example.com', password='password')
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('roles', response.context_data)
        self.assertEqual(list(response.context_data['roles']), [self.group])

class Error404ViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_error404_view_context(self):
        request = self.factory.get('/nonexistent-url/')
        response = Error404View.as_view()(request)
        self.assertEqual(response.context_data['error_code'], 404)
        self.assertEqual(response.context_data['error_message'], 'Página no encontrada')
        self.assertEqual(response.context_data['error_description'], 'La página que estás buscando no existe o fue movida.')

class Error500ViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_error500_view_status_code(self):
        request = self.factory.get('/error-500/')
        response = Error500View.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_error500_view_context(self):
        request = self.factory.get('/error-500/')
        response = Error500View.as_view()(request)
        self.assertEqual(response.context_data['error_code'], 500)
        self.assertEqual(response.context_data['error_message'], 'Error interno del servidor')
        self.assertEqual(response.context_data['error_description'], 'Ocurrió un problema con el servidor. Estamos trabajando para resolverlo.')

class Error403ViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_error403_view_status_code(self):
        request = self.factory.get('/error-403/')
        response = Error403View.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_error403_view_context(self):
        request = self.factory.get('/error-403/')
        response = Error403View.as_view()(request)
        self.assertEqual(response.context_data['error_code'], 403)
        self.assertEqual(response.context_data['error_message'], 'No tienes permiso para acceder a esta página')
        self.assertEqual(response.context_data['error_description'], 'No tienes permiso para acceder a esta página. Por favor, contacta al administrador.')

class UserEditViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('edit_profile')

    def test_get_object(self):
        response = self.client.get(self.url)
        view = UserEditView()
        view.request = response.wsgi_request
        self.assertEqual(view.get_object(), self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/edit_profile.html')
        self.assertIsInstance(response.context['form'], EditProfileForm)
        self.assertEqual(response.context['form'].instance, self.user)

    def test_post_invalid_data(self):
        data = {
            'username': '',
            'email': 'invalidemail',
            'first_name': '',
            'last_name': '',
            'password': 'testpassword'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/edit_profile.html')
        self.assertFalse(response.context['form'].is_valid())

class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        self.url = reverse('profile')

    def test_access_with_login(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/profile.html')

    def test_context_data(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user)

class PasswordsChangeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='old_password'
        )
        self.client.login(username='testuser', password='old_password')
        self.url = reverse('password_change')

    def test_password_change_view_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/change-password.html')

    def test_password_change_success(self):
        response = self.client.post(self.url, {
            'old_password': 'old_password',
            'new_password1': 'new_password123',
            'new_password2': 'new_password123'
        })
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password123'))

class UserAddRoleViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.client.login(username='testuser', password='12345')
        self.group = Group.objects.create(name='Test Group')
        self.url = reverse('additional_role')

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, "La solicitud GET debería retornar un código de estado 200")
        self.assertTemplateUsed(response, 'members/add_role.html', "La vista debería usar la plantilla 'add_role.html'")
        self.assertIn('form', response.context, "El contexto debería contener el formulario")
        self.assertIn('roles', response.context, "El contexto debería contener los roles disponibles")

    def test_post_request_invalid_data(self):
        invalid_data = {
            'group': ''
        }
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200, "La solicitud POST debería retornar un código de estado 200")
        self.assertFalse(response.context['form'].is_valid(), "El formulario debería ser inválido con datos incorrectos")
        self.assertIn('group', response.context['form'].errors, "El formulario debería contener errores para el campo 'group'")

class UserNotificationsViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Member.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='12345'
        )
        self.client.login(username='testuser', password='12345')
        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')
        self.notification = Notification.objects.create(user=self.user)
        self.url = reverse('notifications')

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, "La solicitud GET debería retornar un código de estado 200")
        self.assertTemplateUsed(response, 'members/notifications.html', "La vista debería usar la plantilla 'notifications.html'")
        self.assertIn('combined_categories', response.context, "El contexto debería contener 'combined_categories'")
        self.assertIn('purchased_categories', response.context, "El contexto debería contener 'purchased_categories'")
        self.assertIn('suscribed_categories', response.context, "El contexto debería contener 'suscribed_categories'")
        self.assertIn('notification', response.context, "El contexto debería contener 'notification'")
        self.assertIn('additional_notifications', response.context, "El contexto debería contener 'additional_notifications'")

    def test_post_toggle_category_notification(self):
        post_data = {
            'action': 'toggle_notification',
            'category_id': self.category1.id
        }
        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, 302, "La solicitud POST debería retornar un código de estado 302")
        self.notification.refresh_from_db()
        self.assertIn(self.category1, self.notification.notifications.all(), "La categoría debería ser agregada a las notificaciones del usuario")

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, 302, "La solicitud POST debería retornar un código de estado 302")
        self.notification.refresh_from_db()
        self.assertNotIn(self.category1, self.notification.notifications.all(), "La categoría debería ser removida de las notificaciones del usuario")
