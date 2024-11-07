from django.test import TestCase, RequestFactory
from posts.models import Category
from members.models import Member
from .models import *
from django.utils import timezone
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .views import *
from unittest.mock import patch

##### PRUEBAS PARA MODELOS #####
class PurchaseModelTest(TestCase):

    def setUp(self):
        self.member = Member.objects.create(username="TestUser")  # Ajusta el campo según corresponda
        self.category = Category.objects.create(name="Test Category")
        self.purchase = Purchase.objects.create(
            user=self.member,
            category=self.category,
            price=100.00,
            date=timezone.now()
        )

    def test_purchase_str(self):
        expected_str = f'El usuario "{self.purchase.user}" compró la categoría "{self.purchase.category}" por ${self.purchase.price} en la fecha y hora {self.purchase.date}'

##### PRUEBAS PARA VISTAS #####
class CustomImageUploadViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = CustomImageUploadView.as_view()

    @patch('django.core.files.storage.default_storage.save')
    @patch('django.core.files.storage.default_storage.url')
    def test_post_image_upload(self, mock_url, mock_save):
        # Mock the save and url methods
        mock_save.return_value = 'test_image.jpg'
        mock_url.return_value = 'http://testserver/media/test_image.jpg'

        # Create a test image file
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

        # Create a POST request with the image file
        request = self.factory.post(reverse('ckeditor_upload'), {'upload': image})

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'uploaded': 1,
            'fileName': 'test_image.jpg',
            'url': 'http://testserver/media/test_image.jpg'
        })

    def test_post_no_file(self):
        # Create a POST request without a file
        request = self.factory.post(reverse('ckeditor_upload'))

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'No se ha proporcionado ningún archivo.'})

class CreateCheckoutSessionViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = CreateCheckoutSessionView.as_view()
        self.category = Category.objects.create(name="Test Category", kind="premium", price=100.00)

    def test_post_non_premium_category(self):
        # Create a non-premium category
        non_premium_category = Category.objects.create(name="Non-Premium Category", kind="free", price=0.00)

        # Create a POST request
        request = self.factory.post(reverse('stripe_checkout', args=[non_premium_category.id]))

        # Call the view
        response = self.view(request, category_id=non_premium_category.id)

        # Check the response
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Esta categoría no es premium'})

    def test_get_method_not_allowed(self):
        # Create a GET request
        request = self.factory.get(reverse('stripe_checkout', args=[self.category.id]))

        # Call the view
        response = self.view(request, category_id=self.category.id)

        # Check the response
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.reason_phrase, 'Method Not Allowed')

class PaymentSuccessViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = PaymentSuccessView.as_view()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name="Test Category", kind="premium", price=100.00)

    def test_get_no_session_id(self):
        request = self.factory.get(reverse('payment_success'))
        request.user = self.user

        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'No session_id provided'})

class PaymentCancelViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = PaymentCancelView.as_view()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name="Test Category", kind="premium", price=100.00)

    def add_middleware(self, request):
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)
        request.session.save()

    def test_get_payment_cancel(self):
        # Create a GET request
        request = self.factory.get(reverse('payment_cancel', args=[self.category.id]))
        request.user = self.user

        # Add middleware to the request
        self.add_middleware(request)

        # Call the view
        response = self.view(request, category_id=self.category.id)

        # Check the response
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.category.get_absolute_url())

        # Check that the warning message was added
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'El pago fue cancelado. Puedes intentar de nuevo.')

class DashboardClapsPostsViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = DashboardClapsPostsView.as_view()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(title="Test Post", author=self.user, category=self.category)

    @patch('requests.get')
    def test_get_context_data(self, mock_get):
        # Mock the API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                'data': {
                    'id': str(self.post.id),
                    'attributes': {
                        'total_claps': 10
                    }
                }
            }
        ]

        # Create a GET request
        request = self.factory.get(reverse('posts_claps'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('clap_data', response.context_data)
        self.assertEqual(len(response.context_data['clap_data']), 1)
        self.assertEqual(response.context_data['clap_data'][0]['id'], str(self.post.id))
        self.assertEqual(response.context_data['clap_data'][0]['total_claps'], 10)
        self.assertEqual(response.context_data['clap_data'][0]['title'], self.post.title)
        self.assertEqual(response.context_data['clap_data'][0]['author'], self.post.author)
        self.assertEqual(response.context_data['clap_data'][0]['category'], self.post.category)

class DashboardUpdownsPostsViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = DashboardUpdownsPostsView.as_view()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(title="Test Post", author=self.user, category=self.category)

    @patch('requests.get')
    def test_get_context_data(self, mock_get):
        # Mock the API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                'data': {
                    'id': str(self.post.id),
                    'attributes': {
                        'total_score': 5
                    }
                }
            }
        ]

        # Create a GET request
        request = self.factory.get(reverse('posts_updowns'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('updown_data', response.context_data)
        self.assertEqual(len(response.context_data['updown_data']), 1)
        self.assertEqual(response.context_data['updown_data'][0]['id'], str(self.post.id))
        self.assertEqual(response.context_data['updown_data'][0]['total_score'], 5)
        self.assertEqual(response.context_data['updown_data'][0]['title'], self.post.title)
        self.assertEqual(response.context_data['updown_data'][0]['author'], self.post.author)
        self.assertEqual(response.context_data['updown_data'][0]['category'], self.post.category)

class DashboardRatePostsViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = DashboardRatePostsView.as_view()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(title="Test Post", author=self.user, category=self.category)

    @patch('requests.get')
    def test_get_context_data(self, mock_get):
        # Mock the API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'data': {
                'attributes': {
                    'responses': [
                        {
                            'data': {
                                'type': 'rate_button',
                                'id': str(self.post.id),
                                'attributes': {
                                    'average_rating': 4.5,
                                    'total_votes': 10
                                }
                            }
                        }
                    ]
                }
            }
        }

        # Create a GET request
        request = self.factory.get(reverse('posts_rates'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('rate_data', response.context_data)
        self.assertEqual(len(response.context_data['rate_data']), 1)
        self.assertEqual(response.context_data['rate_data'][0]['id'], str(self.post.id))
        self.assertEqual(response.context_data['rate_data'][0]['average_rating'], 4.5)
        self.assertEqual(response.context_data['rate_data'][0]['total_votes'], 10)
        self.assertEqual(response.context_data['rate_data'][0]['title'], self.post.title)
        self.assertEqual(response.context_data['rate_data'][0]['author'], self.post.author)
        self.assertEqual(response.context_data['rate_data'][0]['category'], self.post.category)

    @patch('requests.get')
    def test_get_context_data_no_rates(self, mock_get):
        # Mock the API response with no rate buttons
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'data': {
                'attributes': {
                    'responses': []
                }
            }
        }

        # Create a GET request
        request = self.factory.get(reverse('posts_rates'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('rate_data', response.context_data)
        self.assertEqual(len(response.context_data['rate_data']), 0)

class DashboardClapsCategoriesViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = DashboardClapsCategoriesView.as_view()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(title="Test Post", author=self.user, category=self.category)

    @patch('requests.get')
    def test_get_context_data(self, mock_get):
        # Mock the API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'data': [
                {
                    'id': str(self.post.id),
                    'attributes': {
                        'total_claps': 10
                    }
                }
            ]
        }

        # Create a GET request
        request = self.factory.get(reverse('categories_claps'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('category_clap_data', response.context_data)
        self.assertEqual(len(response.context_data['category_clap_data']), 1)
        category_clap_data = list(response.context_data['category_clap_data'])[0]
        self.assertEqual(category_clap_data['id'], self.category.id)
        self.assertEqual(category_clap_data['name'], self.category.name)
        self.assertEqual(category_clap_data['total_claps'], 10)

    @patch('requests.get')
    def test_get_context_data_no_claps(self, mock_get):
        # Mock the API response with no claps
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': []}

        # Create a GET request
        request = self.factory.get(reverse('categories_claps'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('category_clap_data', response.context_data)
        self.assertEqual(len(response.context_data['category_clap_data']), 0)

class DashboardUpdownsCategoriesViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = DashboardUpdownsCategoriesView.as_view()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(title="Test Post", author=self.user, category=self.category)

    @patch('requests.get')
    def test_get_context_data(self, mock_get):
        # Mock the API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'data': [
                {
                    'id': str(self.post.id),
                    'attributes': {
                        'total_score': 5
                    }
                }
            ]
        }

        # Create a GET request
        request = self.factory.get(reverse('categories_updowns'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('category_updown_data', response.context_data)
        self.assertEqual(len(response.context_data['category_updown_data']), 1)
        category_updown_data = list(response.context_data['category_updown_data'])[0]
        self.assertEqual(category_updown_data['id'], self.category.id)
        self.assertEqual(category_updown_data['name'], self.category.name)
        self.assertEqual(category_updown_data['total_updowns'], 5)

    @patch('requests.get')
    def test_get_context_data_no_updowns(self, mock_get):
        # Mock the API response with no updowns
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': []}

        # Create a GET request
        request = self.factory.get(reverse('categories_updowns'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('category_updown_data', response.context_data)
        self.assertEqual(len(response.context_data['category_updown_data']), 0)

class DashboardRateCategoriesViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = DashboardRateCategoriesView.as_view()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(title="Test Post", author=self.user, category=self.category)

    @patch('requests.get')
    def test_get_context_data(self, mock_get):
        # Mock the API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'data': {
                'attributes': {
                    'responses': [
                        {
                            'data': {
                                'type': 'rate_button',
                                'id': str(self.post.id),
                                'attributes': {
                                    'average_rating': 4.5,
                                    'total_votes': 10
                                }
                            }
                        }
                    ]
                }
            }
        }

        # Create a GET request
        request = self.factory.get(reverse('categories_rates'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('category_rate_data', response.context_data)
        self.assertEqual(len(response.context_data['category_rate_data']), 1)
        category_rate_data = list(response.context_data['category_rate_data'])[0]
        self.assertEqual(category_rate_data['id'], self.category.id)
        self.assertEqual(category_rate_data['name'], self.category.name)
        self.assertEqual(category_rate_data['average_rating'], 4.5)
        self.assertEqual(category_rate_data['total_votes'], 1)

    @patch('requests.get')
    def test_get_context_data_no_rates(self, mock_get):
        # Mock the API response with no rate buttons
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'data': {
                'attributes': {
                    'responses': []
                }
            }
        }

        # Create a GET request
        request = self.factory.get(reverse('categories_rates'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('category_rate_data', response.context_data)
        self.assertEqual(len(response.context_data['category_rate_data']), 0)

class DashboardPostsViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = DashboardPostsView.as_view()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category = Category.objects.create(name="Test Category", kind="premium")
        self.post = Post.objects.create(title="Test Post", author=self.user, category=self.category)

    @patch('requests.get')
    def test_get_context_data(self, mock_get):
        # Mock the API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'data': {
                'attributes': {
                    'responses': [
                        {
                            'data': {
                                'type': 'clap_button',
                                'id': str(self.post.id),
                                'attributes': {
                                    'total_claps': 10
                                }
                            }
                        },
                        {
                            'data': {
                                'type': 'updown_button',
                                'id': str(self.post.id),
                                'attributes': {
                                    'total_score': 5
                                }
                            }
                        },
                        {
                            'data': {
                                'type': 'rate_button',
                                'id': str(self.post.id),
                                'attributes': {
                                    'average_rating': 4.5,
                                    'total_votes': 10
                                }
                            }
                        }
                    ]
                }
            }
        }

        # Create a GET request
        request = self.factory.get(reverse('engagement_dashboard'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('clap_data', response.context_data)
        self.assertIn('updown_data', response.context_data)
        self.assertIn('rating_data', response.context_data)
        self.assertIn('total_updowns', response.context_data)
        self.assertIn('total_claps', response.context_data)
        self.assertIn('average_rating', response.context_data)
        self.assertIn('views_by_kind', response.context_data)

        # Check the aggregated data
        self.assertEqual(response.context_data['total_claps'], 10)
        self.assertEqual(response.context_data['total_updowns'], 5)
        self.assertEqual(response.context_data['average_rating'], 4.5)
        self.assertEqual(response.context_data['views_by_kind']['premium'], 10)

    @patch('requests.get')
    def test_get_context_data_no_data(self, mock_get):
        # Mock the API response with no data
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'data': {
                'attributes': {
                    'responses': []
                }
            }
        }

        # Create a GET request
        request = self.factory.get(reverse('engagement_dashboard'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('clap_data', response.context_data)
        self.assertIn('updown_data', response.context_data)
        self.assertIn('rating_data', response.context_data)
        self.assertIn('total_updowns', response.context_data)
        self.assertIn('total_claps', response.context_data)
        self.assertIn('average_rating', response.context_data)
        self.assertIn('views_by_kind', response.context_data)

        # Check the aggregated data
        self.assertEqual(response.context_data['total_claps'], 0)
        self.assertEqual(response.context_data['total_updowns'], 0)
        self.assertEqual(response.context_data['average_rating'], 0)
        self.assertEqual(response.context_data['views_by_kind']['premium'], 0)

class SendLoginEmailViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = SendLoginEmailView()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')

    def test_get_client_ip(self):
        # Create a mock request with HTTP_X_FORWARDED_FOR
        request = self.factory.get('/fake-url')
        request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.1'
        ip = self.view.get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')

        # Create a mock request without HTTP_X_FORWARDED_FOR
        request = self.factory.get('/fake-url')
        request.META['REMOTE_ADDR'] = '127.0.0.2'
        ip = self.view.get_client_ip(request)
        self.assertEqual(ip, '127.0.0.2')

class FinancesMembersViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = FinancesMembersView.as_view()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category1 = Category.objects.create(name="Category 1", kind="premium")
        self.category2 = Category.objects.create(name="Category 2", kind="premium")
        self.purchase1 = Purchase.objects.create(user=self.user, category=self.category1, price=50.00)
        self.purchase2 = Purchase.objects.create(user=self.user, category=self.category2, price=100.00)

    def test_get_context_data(self):
        # Create a GET request
        request = self.factory.get(reverse('members_finances'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('purchases', response.context_data)
        self.assertIn('categories', response.context_data)

        # Check the context data
        purchases = response.context_data['purchases']
        categories = response.context_data['categories']
        self.assertEqual(len(purchases), 2)
        self.assertEqual(len(categories), 2)
        self.assertEqual(purchases[0].category.name, 'Category 1')
        self.assertEqual(purchases[0].price, 50.00)
        self.assertEqual(purchases[1].category.name, 'Category 2')
        self.assertEqual(purchases[1].price, 100.00)

class FinancesCategoriesViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = FinancesCategoriesView.as_view()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")
        self.purchase1 = Purchase.objects.create(user=self.user, category=self.category1, price=50.00)
        self.purchase2 = Purchase.objects.create(user=self.user, category=self.category2, price=100.00)

    def test_get_context_data(self):
        # Create a GET request
        request = self.factory.get(reverse('categories_finances'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('categories', response.context_data)

        # Check the context data
        categories = response.context_data['categories']
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0]['category__name'], 'Category 1')
        self.assertEqual(categories[0]['total'], 50.00)
        self.assertEqual(categories[1]['category__name'], 'Category 2')
        self.assertEqual(categories[1]['total'], 100.00)

class MemberPurchaseViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = MemberPurchaseView.as_view()
        self.user = Member.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")
        self.purchase1 = Purchase.objects.create(user=self.user, category=self.category1, price=50.00)
        self.purchase2 = Purchase.objects.create(user=self.user, category=self.category2, price=100.00)

    def test_get_context_data(self):
        # Create a GET request
        request = self.factory.get(reverse('member_purchase'))
        request.user = self.user

        # Call the view
        response = self.view(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn('categories', response.context_data)
        self.assertIn('total_sum', response.context_data)
        self.assertIn('total_categories', response.context_data)

        # Check the context data
        categories = response.context_data['categories']
        total_sum = response.context_data['total_sum']
        total_categories = response.context_data['total_categories']

        self.assertEqual(len(categories), 2)
        self.assertEqual(total_sum, 150.00)
        self.assertEqual(total_categories, 2)