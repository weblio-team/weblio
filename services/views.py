from django.http import Http404, HttpRequest, JsonResponse
from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from posts.models import Post, Category
from django.http import HttpResponseNotAllowed
from django.contrib import messages
import requests
from django.views.generic import TemplateView
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
import platform
from django.contrib.auth.views import PasswordResetView
from dicts import translated_module_dict, translated_submodule_dict, translated_permission_dict
from .models import Purchase
from django.db import models
import json
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.contrib.sites.models import Site

class CustomImageUploadView(View):
    """
    Vista personalizada para la subida de imágenes.

    Esta vista permite subir imágenes a Google Cloud Storage a través de una solicitud POST.
    La vista está exenta de la protección CSRF.

    Métodos:
    --------
    dispatch(*args, **kwargs):
        Maneja la distribución de la solicitud, exenta de la protección CSRF.
    post(request, *args, **kwargs):
        Maneja la solicitud POST para subir una imagen.
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """
        Maneja la distribución de la solicitud, exenta de la protección CSRF.

        Parameters:
        -----------
        *args : list
            Argumentos posicionales.
        **kwargs : dict
            Argumentos de palabras clave.

        Returns:
        --------
        HttpResponse
            La respuesta HTTP resultante de la distribución de la solicitud.
        """
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Maneja la solicitud POST para subir una imagen.

        Verifica si el archivo está presente en la solicitud, guarda el archivo en Google Cloud Storage
        y devuelve la URL del archivo subido. Si ocurre un error, devuelve un mensaje de error.

        Parameters:
        -----------
        request : HttpRequest
            La solicitud HTTP que contiene el archivo a subir.
        *args : list
            Argumentos posicionales.
        **kwargs : dict
            Argumentos de palabras clave.

        Returns:
        --------
        JsonResponse
            La respuesta JSON que contiene la URL del archivo subido o un mensaje de error.
        """
        # Verificar si el archivo está presente
        if 'upload' not in request.FILES:
            return JsonResponse({'error': 'No se ha proporcionado ningún archivo.'}, status=400)

        # Obtener el archivo subido desde la solicitud
        upload = request.FILES['upload']
        print(f"Subiendo archivo: {upload.name}")

        # Guardar el archivo en Google Cloud Storage
        try:
            file_path = default_storage.save(f"{upload.name}", upload)
            print(f"Ruta del archivo guardado: {file_path}")

            # Obtener la URL del archivo subido
            file_url = default_storage.url(file_path)
            print(f"URL del archivo: {file_url}")

            return JsonResponse({
                'uploaded': 1,
                'fileName': upload.name,
                'url': file_url
            })

        except Exception as e:
            print(f"Error al subir el archivo: {str(e)}")
            return JsonResponse({'error': 'Error al subir el archivo.'}, status=500)

# Configuración de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Clase para crear la sesión de Stripe
@method_decorator(csrf_exempt, name='dispatch')
class CreateCheckoutSessionView(View):
    """
    Vista para crear una sesión de pago en Stripe.

    Esta vista maneja la creación de una sesión de pago en Stripe para una categoría premium.

    Métodos:
    --------
    post(request, category_id, *args, **kwargs):
        Maneja la solicitud POST para crear una sesión de pago en Stripe.
    get(request, *args, **kwargs):
        Maneja la solicitud GET devolviendo un 405 (Método no permitido).
    """
    def post(self, request, category_id, *args, **kwargs):
        """
        Maneja la solicitud POST para crear una sesión de pago en Stripe.

        Args:
        -----
        request : HttpRequest
            La solicitud HTTP.
        category_id : int
            El ID de la categoría para la cual se desea crear la sesión de pago.

        Returns:
        --------
        JsonResponse
            Redirige al cliente a la página de pago de Stripe o devuelve un error en caso de fallo.
        """
        category = get_object_or_404(Category, pk=category_id)

        if category.kind != 'premium':
            return JsonResponse({'error': 'Esta categoría no es premium'}, status=400)

        try:
            # Crear la sesión de Stripe
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': category.name,
                        },
                        'unit_amount': int(category.price * 100),  # Convertir el precio a centavos
                    },
                    'quantity': 1,
                }],
                mode='payment',
                metadata={
                    'category_id': str(category.pk),  # Asegúrate de incluir el category_id aquí
                    'category_name': category.name
                },
                success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url = request.build_absolute_uri(reverse('payment_cancel', kwargs={'category_id': category.pk})),            )
            # Redirigir al cliente a la página de pago de Stripe
            return redirect(session.url, code=303)

        except stripe.error.StripeError as e:
            # Capturar los errores de Stripe
            return JsonResponse({'error': str(e)}, status=500)

        except Exception as e:
            # Capturar otros posibles errores
            return JsonResponse({'error': str(e)}, status=500)
    
    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud GET devolviendo un 405 (Método no permitido).

        Args:
        -----
        request : HttpRequest
            La solicitud HTTP.

        Returns:
        --------
        HttpResponseNotAllowed
            Respuesta HTTP indicando que el método GET no está permitido.
        """
        # Si llega una solicitud GET, devolver un 405 (Método no permitido)
        return HttpResponseNotAllowed(['POST'])

# Clase para manejar la confirmación del pago
@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessView(View):
    """
    Vista para manejar la confirmación del pago exitoso.

    Esta vista maneja la confirmación del pago exitoso de una categoría premium,
    agregando la categoría a las compradas por el usuario y creando un registro de la compra.

    Métodos:
    --------
    get(request, *args, **kwargs):
        Maneja la solicitud GET para confirmar el pago exitoso.
    """
    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud GET para confirmar el pago exitoso.

        Args:
        -----
        request : HttpRequest
            La solicitud HTTP.
        *args : list
            Argumentos posicionales.
        **kwargs : dict
            Argumentos clave.

        Returns:
        --------
        JsonResponse or HttpResponseRedirect
            Devuelve una respuesta JSON en caso de error o redirige a la página de la categoría en caso de éxito.
        """
        session_id = request.GET.get('session_id')
        if not session_id:
            return JsonResponse({'error': 'No session_id provided'}, status=400)

        # Obtener la sesión de Stripe
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            print(f"Stripe session retrieved: {session}")
        except stripe.error.StripeError as e:
            print(f"Error retrieving Stripe session: {e}")
            return JsonResponse({'error': 'Error retrieving Stripe session'}, status=500)

        # Obtener el usuario actual
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'error': 'User is not authenticated'}, status=401)

        try:
            # Verificar si los metadata contienen el category_id
            if 'category_id' in session['metadata']:
                category_id = session['metadata']['category_id']
                print(f"Category ID retrieved from metadata: {category_id}")

                # Verificar si la categoría existe
                category = get_object_or_404(Category, pk=category_id)
                print(f"Category found: {category.name}")

                # Agregar la categoría a las compradas por el usuario
                user.purchased_categories.add(category)
                user.save()
                print(f"Category {category.name} added to user {user.username}'s purchased categories.")

                # Crear una nueva instancia de Purchase
                purchase = Purchase(
                    user=user,
                    category=category,
                    price=session['amount_total'] / 100,  # Stripe amount is in cents
                )
                purchase.save()
                print(f"Purchase record created: {purchase}")
                print(f"User {user.username} purchased category {category.name} for ${purchase.price}")

                # Mostrar mensaje de éxito
                messages.success(request, '¡Categoría comprada con éxito!')

                # Redirigir a la página de la categoría
                return redirect(category.get_absolute_url())
            else:
                return JsonResponse({'error': 'Category ID not found in metadata'}, status=500)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': 'Error processing payment success'}, status=500)

# Clase para manejar el cancelamiento del pago
@method_decorator(csrf_exempt, name='dispatch')
class PaymentCancelView(View):
    """
    Vista para manejar la cancelación del pago.

    Esta vista maneja la cancelación del pago de una categoría, mostrando un mensaje de advertencia
    y redirigiendo al usuario a la página de la categoría correspondiente.

    Métodos:
    --------
    get(request, category_id, *args, **kwargs):
        Maneja la solicitud GET para cancelar el pago.
    """
    def get(self, request, category_id, *args, **kwargs):
        """
        Maneja la solicitud GET para cancelar el pago.

        Args:
        -----
        request : HttpRequest
            La solicitud HTTP.
        category_id : int
            El ID de la categoría para la cual se desea cancelar el pago.
        *args : list
            Argumentos posicionales.
        **kwargs : dict
            Argumentos clave.

        Returns:
        --------
        HttpResponseRedirect
            Redirige al usuario a la página de la categoría correspondiente.
        """
        # Obtener la categoría usando el category_id
        category = get_object_or_404(Category, pk=category_id)

        # Mostrar un mensaje de cancelación usando el sistema de mensajes de Django
        messages.warning(request, 'El pago fue cancelado. Puedes intentar de nuevo.')

        # Redirigir al usuario a la página de la categoría correspondiente
        return redirect(category.get_absolute_url())

class DashboardClapsPostsView(TemplateView):
    """
    Vista del reporte de views de los articulos.
    """
    template_name = 'dashboard/posts/claps.html'
    
    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        
        # Adding existing context data
        context['LYKET_API_KEY'] = settings.LYKET_API_KEY
        context['DEBUG'] = settings.DEBUG

        # API Call to Lyket
        url = 'https://api.lyket.dev/v1/rank/clap-buttons?sort=asc&limit=100'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {settings.LYKET_API_KEY}'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # Handle 200 response format
                clap_data = response.json()  # Parse the JSON response
                enriched_clap_data = []

                if isinstance(clap_data, list) and 'data' in clap_data[0]:
                    # For 200 status code, process each item
                    for item in clap_data:
                        clap_button = {'id': item['data']['id'], 'total_claps': item['data']['attributes']['total_claps']}
                        
                        # Fetch the related Post by id
                        try:
                            post = Post.objects.get(id=clap_button['id'])
                            if self.request.user.has_perm('posts.add_post') and post.author == self.request.user:
                                continue  # Skip posts not authored by the user if they have the add_post permission
                            clap_button['title'] = post.title  # Post title
                            clap_button['author'] = post.author  # Post author
                            clap_button['category'] = post.category  # Post category
                        except Post.DoesNotExist:
                            clap_button['title'] = 'Unknown Title'
                            clap_button['author'] = 'Unknown Author'
                            clap_button['category'] = 'Unknown Category'  # Default if post doesn't exist
                        
                        enriched_clap_data.append(clap_button)

                    context['clap_data'] = enriched_clap_data  # Pass enriched data to context
                else:
                    context['clap_data'] = []  # No valid data found
            elif response.status_code == 201:
                # Handle 201 response format (array with data)
                clap_data = response.json()
                enriched_clap_data = []

                for item in clap_data['data']:
                    clap_button = {'id': item['id'], 'total_claps': item['attributes']['total_claps']}
                    
                    # Fetch the related Post by id
                    try:
                        post = Post.objects.get(id=clap_button['id'])
                        if self.request.user.has_perm('posts.add_post') and post.author == self.request.user:
                            continue  # Skip posts not authored by the user if they have the add_post permission
                        clap_button['title'] = post.title  # Post title
                        clap_button['author'] = post.author  # Post author
                        clap_button['category'] = post.category  # Post category
                    except Post.DoesNotExist:
                        clap_button['title'] = 'Unknown Title'
                        clap_button['author'] = 'Unknown Author'
                        clap_button['category'] = 'Unknown Category'
                    
                    enriched_clap_data.append(clap_button)

                context['clap_data'] = enriched_clap_data  # Pass enriched data to context
            else:
                context['clap_data'] = []  # Empty list if there is an error
                context['raw_api_response'] = f"Error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            context['clap_data'] = []  # Empty list in case of exception
            context['raw_api_response'] = f"Request error: {e}"
        
        return context

class DashboardUpdownsPostsView(TemplateView):
    """
    Vista del reporte de updown de los artículos.
    """
    template_name = 'dashboard/posts/updowns.html'
    
    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        
        # Adding existing context data
        context['LYKET_API_KEY'] = settings.LYKET_API_KEY
        context['DEBUG'] = settings.DEBUG

        # API Call to Lyket
        url = 'https://api.lyket.dev/v1/rank/updown-buttons?sort=asc&limit=100'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {settings.LYKET_API_KEY}'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                updown_data = response.json()  # Parse the JSON response
                enriched_updown_data = []

                if isinstance(updown_data, list) and 'data' in updown_data[0]:
                    # Process each updown button data
                    for item in updown_data:
                        updown_button = {
                            'id': item['data']['id'],
                            'total_score': item['data']['attributes'].get('total_score', 0)
                        }

                        # Fetch the related Post by id
                        try:
                            post = Post.objects.get(id=updown_button['id'])
                            if self.request.user.has_perm('posts.add_post') and post.author == self.request.user:
                                continue  # Skip posts not authored by the user if they have the add_post permission
                            updown_button['title'] = post.title  # Post title
                            updown_button['author'] = post.author  # Post author
                            updown_button['category'] = post.category  # Post category
                        except Post.DoesNotExist:
                            updown_button['title'] = 'Unknown Title'
                            updown_button['author'] = 'Unknown Author'
                            updown_button['category'] = 'Unknown Category'
                        
                        enriched_updown_data.append(updown_button)

                    context['updown_data'] = enriched_updown_data
                else:
                    context['updown_data'] = []
            elif response.status_code == 201:
                updown_data = response.json()
                enriched_updown_data = []

                for item in updown_data['data']:
                    updown_button = {
                        'id': item['id'],
                        'total_score': item['attributes'].get('total_score', 0)
                    }

                    # Fetch the related Post by id
                    try:
                        post = Post.objects.get(id=updown_button['id'])
                        if self.request.user.has_perm('posts.add_post') and post.author == self.request.user:
                            continue  # Skip posts not authored by the user if they have the add_post permission
                        updown_button['title'] = post.title  # Post title
                        updown_button['author'] = post.author  # Post author
                        updown_button['category'] = post.category  # Post category
                    except Post.DoesNotExist:
                        updown_button['title'] = 'Unknown Title'
                        updown_button['author'] = 'Unknown Author'
                        updown_button['category'] = 'Unknown Category'
                    
                    enriched_updown_data.append(updown_button)

                context['updown_data'] = enriched_updown_data
            else:
                context['updown_data'] = []
                context['raw_api_response'] = f"Error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            context['updown_data'] = []
            context['raw_api_response'] = f"Request error: {e}"
        
        return context
    
class DashboardRatePostsView(TemplateView):
    """
    Vista del reporte de botones de calificación de los artículos (solo rate_button).
    """
    template_name = 'dashboard/posts/rates.html'
    
    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        
        # Adding existing context data
        context['LYKET_API_KEY'] = settings.LYKET_API_KEY
        context['DEBUG'] = settings.DEBUG

        # API Call to Lyket for rate buttons (filtered by "type": "rate_button")
        url = 'https://api.lyket.dev/v1/rank/buttons/blog?sort=desc&limit=100'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {settings.LYKET_API_KEY}'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code in [200, 201]:
                rate_data = response.json()  # Parse the JSON response
                enriched_rate_data = []

                # Process each button and filter for only "rate_button" types
                for item in rate_data['data']['attributes']['responses']:
                    if item['data']['type'] == 'rate_button':
                        rate_button = {
                            'id': item['data']['id'],
                            'average_rating': item['data']['attributes'].get('average_rating', 0),
                            'total_votes': item['data']['attributes'].get('total_votes', 0)
                        }

                        # Fetch the related Post by id
                        try:
                            post = Post.objects.get(id=rate_button['id'])
                            if self.request.user.has_perm('posts.add_post') and post.author == self.request.user:
                                continue  # Skip posts not authored by the user if they have the add_post permission
                            rate_button['title'] = post.title  # Post title
                            rate_button['author'] = post.author  # Post author
                            rate_button['category'] = post.category  # Post category
                        except Post.DoesNotExist:
                            rate_button['title'] = 'Unknown Title'
                            rate_button['author'] = 'Unknown Author'
                            rate_button['category'] = 'Unknown Category'
                        
                        enriched_rate_data.append(rate_button)

                context['rate_data'] = enriched_rate_data
            else:
                context['rate_data'] = []  # Empty list if there is an error
                context['raw_api_response'] = f"Error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            context['rate_data'] = []  # Empty list in case of exception
            context['raw_api_response'] = f"Request error: {e}"
        
        return context


class DashboardClapsCategoriesView(TemplateView):
    """
    Vista del reporte de claps por categorías.
    """
    template_name = 'dashboard/categories/claps.html'
    
    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        
        # Adding existing context data
        context['LYKET_API_KEY'] = settings.LYKET_API_KEY
        context['DEBUG'] = settings.DEBUG

        # API Call to Lyket
        url = 'https://api.lyket.dev/v1/rank/clap-buttons?sort=asc&limit=100'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {settings.LYKET_API_KEY}'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code in [200, 201]:
                clap_data = response.json()  # Parse the JSON response
                category_clap_data = {}

                for item in clap_data['data']:
                    post_id = item['id']
                    total_claps = item['attributes']['total_claps']
                    
                    try:
                        post = Post.objects.get(id=post_id)
                        category = post.category
                        if category.id not in category_clap_data:
                            category_clap_data[category.id] = {
                                'id': category.id,
                                'name': category.name,
                                'total_claps': 0
                            }
                        category_clap_data[category.id]['total_claps'] += total_claps
                    except Post.DoesNotExist:
                        continue

                context['category_clap_data'] = category_clap_data.values()
            else:
                context['category_clap_data'] = []
                context['raw_api_response'] = f"Error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            context['category_clap_data'] = []
            context['raw_api_response'] = f"Request error: {e}"
        
        return context

class DashboardUpdownsCategoriesView(TemplateView):
    """
    Vista del reporte de updowns por categorías.
    """
    template_name = 'dashboard/categories/updowns.html'
    
    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        
        # Adding existing context data
        context['LYKET_API_KEY'] = settings.LYKET_API_KEY
        context['DEBUG'] = settings.DEBUG

        # API Call to Lyket
        url = 'https://api.lyket.dev/v1/rank/updown-buttons?sort=asc&limit=100'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {settings.LYKET_API_KEY}'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code in [200, 201]:
                updown_data = response.json()  # Parse the JSON response
                category_updown_data = {}

                for item in updown_data['data']:
                    post_id = item['id']
                    total_score = item['attributes'].get('total_score', 0)
                    
                    try:
                        post = Post.objects.get(id=post_id)
                        category = post.category
                        if category.id not in category_updown_data:
                            category_updown_data[category.id] = {
                                'id': category.id,
                                'name': category.name,
                                'total_updowns': 0
                            }
                        category_updown_data[category.id]['total_updowns'] += total_score
                    except Post.DoesNotExist:
                        continue

                context['category_updown_data'] = category_updown_data.values()
            else:
                context['category_updown_data'] = []
                context['raw_api_response'] = f"Error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            context['category_updown_data'] = []
            context['raw_api_response'] = f"Request error: {e}"
        
        return context
    
class DashboardRateCategoriesView(TemplateView):
    """
    Vista del reporte de botones de calificación por categorías.
    """
    template_name = 'dashboard/categories/rates.html'
    
    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto de la plantilla."""
        context = super().get_context_data(**kwargs)
        
        # Adding existing context data
        context['LYKET_API_KEY'] = settings.LYKET_API_KEY
        context['DEBUG'] = settings.DEBUG

        # API Call to Lyket for rate buttons (filtered by "type": "rate_button")
        url = 'https://api.lyket.dev/v1/rank/buttons/blog?sort=desc&limit=100'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {settings.LYKET_API_KEY}'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code in [200, 201]:
                rate_data = response.json()  # Parse the JSON response
                category_rate_data = {}

                for item in rate_data['data']['attributes']['responses']:
                    if item['data']['type'] == 'rate_button':
                        post_id = item['data']['id']
                        average_rating = item['data']['attributes'].get('average_rating', 0)
                        
                        try:
                            post = Post.objects.get(id=post_id)
                            category = post.category
                            if category.id not in category_rate_data:
                                category_rate_data[category.id] = {
                                    'id': category.id,
                                    'name': category.name,
                                    'average_rating': 0,
                                    'total_votes': 0
                                }
                            category_rate_data[category.id]['average_rating'] += average_rating
                            category_rate_data[category.id]['total_votes'] += 1
                        except Post.DoesNotExist:
                            continue

                # Calculate the average rating for each category
                for category in category_rate_data.values():
                    if category['total_votes'] > 0:
                        category['average_rating'] /= category['total_votes']

                context['category_rate_data'] = category_rate_data.values()
            else:
                context['category_rate_data'] = []
                context['raw_api_response'] = f"Error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            context['category_rate_data'] = []
            context['raw_api_response'] = f"Request error: {e}"
        
        return context

class DashboardPostsView(TemplateView):
    """
    Vista del dashboard mostrando la comparación de claps, updowns, rates, y estadística de views por tipo de categoría.
    """
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adding existing context data
        context['LYKET_API_KEY'] = settings.LYKET_API_KEY
        context['DEBUG'] = settings.DEBUG

        # Initialize total stats
        total_updowns = 0  # Sum of total_score for all updown buttons
        total_claps = 0
        total_rating = 0
        total_rate_votes = 0

        # Initialize views by kind (public, free, premium)
        views_by_kind = {"public": 0, "free": 0, "premium": 0}

        # Get all categories from the posts
        all_categories = Category.objects.all()  # Get all categories
        category_claps = {category.name: 0 for category in all_categories}  # Initialize claps for each category
        category_updowns = {category.name: 0 for category in all_categories}  # Initialize updowns for each category
        category_ratings = {category.name: {"total_rating": 0, "total_votes": 0} for category in all_categories}  # Initialize ratings

        # API Call to Lyket for all button types
        url = 'https://api.lyket.dev/v1/rank/buttons?sort=desc&limit=100'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {settings.LYKET_API_KEY}'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code in [200, 201]:
                button_data = response.json()  # Parse the JSON response

                # Process each button and aggregate based on category
                for item in button_data['data']['attributes']['responses']:
                    button_type = item['data']['type']
                    attributes = item['data']['attributes']
                    post_id = item['data']['id']

                    # Fetch related Post and its category
                    try:
                        post = Post.objects.get(id=post_id)
                        category = post.category
                    except Post.DoesNotExist:
                        continue  # Skip posts that do not exist

                    # Aggregate views by category kind
                    if category.kind in views_by_kind:
                        views_by_kind[category.kind] += attributes.get('total_claps', 0)

                    # For clap_button
                    if button_type == 'clap_button':
                        total_claps += attributes.get('total_claps', 0)  # Aggregate total claps
                        category_claps[category.name] += attributes.get('total_claps', 0)  # Aggregate claps for the category

                    # For updown_button
                    elif button_type == 'updown_button':
                        total_updowns += attributes.get('total_score', 0)  # Aggregate total_score for total updowns
                        category_updowns[category.name] += attributes.get('total_score', 0)  # Aggregate updowns for the category

                    # For rate_button
                    elif button_type == 'rate_button':
                        total_votes = attributes.get('total_votes', 0)
                        average_rating = attributes.get('average_rating', 0)
                        total_rating += average_rating * total_votes
                        total_rate_votes += total_votes
                        category_ratings[category.name]["total_rating"] += average_rating * total_votes
                        category_ratings[category.name]["total_votes"] += total_votes

                # Calculate the average ratings for each category
                category_avg_ratings = {
                    category: (data["total_rating"] / data["total_votes"]) if data["total_votes"] > 0 else 0
                    for category, data in category_ratings.items()
                }

                # Sort categories by claps, updowns, and ratings
                sorted_clap_data = sorted(category_claps.items(), key=lambda x: x[1], reverse=True)
                sorted_updown_data = sorted(category_updowns.items(), key=lambda x: x[1], reverse=True)
                sorted_rating_data = sorted(category_avg_ratings.items(), key=lambda x: x[1], reverse=True)

                # Add total values and category data to the context for the chart and widgets
                context['clap_data'] = sorted_clap_data
                context['updown_data'] = sorted_updown_data
                context['rating_data'] = sorted_rating_data
                context['total_updowns'] = total_updowns  # Sum of total_score for all updown buttons
                context['total_claps'] = total_claps
                context['average_rating'] = total_rating / total_rate_votes if total_rate_votes > 0 else 0

                # Add views by kind (public, free, premium) to the context
                context['views_by_kind'] = views_by_kind

            else:
                context['clap_data'] = []
                context['updown_data'] = []
                context['rating_data'] = []
                context['total_updowns'] = 0
                context['total_claps'] = 0
                context['average_rating'] = 0
                context['views_by_kind'] = {"public": 0, "free": 0, "premium": 0}
                context['raw_api_response'] = f"Error: {response.status_code}"
        except requests.exceptions.RequestException as e:
            context['clap_data'] = []
            context['updown_data'] = []
            context['rating_data'] = []
            context['total_updowns'] = 0
            context['total_claps'] = 0
            context['average_rating'] = 0
            context['views_by_kind'] = {"public": 0, "free": 0, "premium": 0}
            context['raw_api_response'] = f"Request error: {e}"

        return context

class SendLoginEmailView(View):
    """
    Vista encargada de enviar un correo de notificación de inicio de sesión.
    Esta vista envía un correo electrónico formateado en HTML cuando un usuario inicia sesión.
    """

    def send_email(self, user, request):
        # Información del login
        login_time = timezone.now()
        formatted_login_time = login_time.strftime('%Y-%m-%d %H:%M:%S')
        device = platform.system()
        ip_address = self.get_client_ip(request)

        # Renderizar el cuerpo del mensaje con una plantilla HTML
        html_content = render_to_string('emails/login.html', {
            'username': user.username,
            'login_time': formatted_login_time,
            'device': device,
            'ip_address': ip_address,
        })
        plain_message = strip_tags(html_content)  # Texto sin formato, en caso de que el cliente no soporte HTML
        subject = 'Notificación de inicio de sesión'

        # Crear el mensaje de correo
        email = EmailMultiAlternatives(
            subject,
            plain_message,  # Contenido en texto sin formato
            'weblio.team@gmail.com',  # Remitente
            [user.email]  # Destinatario
        )
        email.attach_alternative(html_content, "text/html")  # Adjuntar el contenido en HTML
        email.send()  # Enviar el correo

    def get_client_ip(self, request):
        """
        Obtiene la dirección IP del cliente a partir de la solicitud HTTP.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class CustomPasswordResetView(PasswordResetView):
    """
    Vista personalizada para el restablecimiento de contraseña.

    Esta vista maneja el proceso de restablecimiento de contraseña, enviando un correo electrónico
    con un enlace para restablecer la contraseña. Utiliza plantillas personalizadas para el correo
    electrónico y el formulario de restablecimiento.

    Atributos:
    ----------
    email_template_name : str
        Ruta de la plantilla de correo electrónico en texto plano.
    html_email_template_name : str
        Ruta de la plantilla de correo electrónico en HTML.
    template_name : str
        Ruta de la plantilla del formulario de restablecimiento de contraseña.

    Métodos:
    --------
    send_mail(subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        Envía un correo electrónico con el enlace para restablecer la contraseña.
    """
    email_template_name = 'emails/password-reset/password_reset_email.html'
    html_email_template_name = 'emails/password-reset/password_reset_email.html'  # Añadir HTML para asegurarnos
    template_name = 'emails/password-reset/password_reset_form.html'

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        """
        Envía un correo electrónico con el enlace para restablecer la contraseña.

        Args:
        -----
        subject_template_name : str
            Ruta de la plantilla del asunto del correo electrónico.
        email_template_name : str
            Ruta de la plantilla del cuerpo del correo electrónico en texto plano.
        context : dict
            Contexto para renderizar las plantillas.
        from_email : str
            Dirección de correo electrónico del remitente.
        to_email : str
            Dirección de correo electrónico del destinatario.
        html_email_template_name : str, optional
            Ruta de la plantilla del cuerpo del correo electrónico en HTML (por defecto es None).

        Returns:
        --------
        None
        """
        subject = render_to_string(subject_template_name, context).strip()
        body = render_to_string(email_template_name, context)

        # Crear el correo con texto plano
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])

        # Adjuntar la versión HTML
        if html_email_template_name:
            html_body = render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_body, "text/html")

        # Enviar el correo
        email_message.send()

class AccountStatusEmailView(View):
    """
    Vista para enviar correos electrónicos sobre el estado de la cuenta.

    Esta vista maneja el envío de correos electrónicos para notificar a los usuarios sobre cambios
    en el estado de su cuenta, utilizando plantillas personalizadas para el correo electrónico.

    Atributos:
    ----------
    email_template_name : str
        Ruta de la plantilla de correo electrónico en texto plano.
    html_email_template_name : str
        Ruta de la plantilla de correo electrónico en HTML.

    Métodos:
    --------
    send_account_status_email(user, account_status, to_email):
        Envía un correo electrónico con el estado de la cuenta al usuario.
    """
    email_template_name = 'emails/account-status/account_status_email.html'
    html_email_template_name = 'emails/account-status/account_status_email.html'

    def send_account_status_email(self, user, account_status, to_email):
        """
        Enviar correo como HTML utilizando EmailMultiAlternatives.
        """
        current_site = Site.objects.get_current()
        current_site.domain = settings.SITE_DOMAIN
        site_protocol = settings.SITE_PROTOCOL
        login_url = f"{site_protocol}://{current_site.domain}/members/login/"
        
        context = {
            'user': user,
            'account_status': account_status,
            'login_url': login_url
        }
        subject = f'Tu cuenta ha sido {account_status}'
        body = render_to_string(self.email_template_name, context)

        # Crear el correo con texto plano
        email_message = EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])

        # Adjuntar la versión HTML
        html_body = render_to_string(self.html_email_template_name, context)
        email_message.attach_alternative(html_body, "text/html")

        # Enviar el correo
        email_message.send()

class UserPermissionsEmailView(View):
    """
    Vista para enviar correos electrónicos sobre los permisos de usuario.

    Esta vista maneja el envío de correos electrónicos para notificar a los usuarios sobre
    sus permisos, utilizando plantillas personalizadas para el correo electrónico.

    Atributos:
    ----------
    email_template_name : str
        Ruta de la plantilla de correo electrónico en texto plano.
    html_email_template_name : str
        Ruta de la plantilla de correo electrónico en HTML.

    Métodos:
    --------
    get_translated_permissions(user):
        Obtiene los permisos agrupados y traducidos para un usuario específico.
    send_permissions_email(user, to_email):
        Envía un correo electrónico con los permisos del usuario.
    """
    email_template_name = 'emails/account-status/user_permissions_email.html'
    html_email_template_name = 'emails/account-status/user_permissions_email.html'

    def get_translated_permissions(self, user):
        """
        Obtiene los permisos agrupados y traducidos para un usuario específico.
        """
        grouped_permissions = {}
        for perm in user.user_permissions.all():
            module_name = perm.content_type.app_label.capitalize()
            submodule_name = perm.content_type.model.capitalize()

            # Traducción de módulos y submódulos
            translated_module = translated_module_dict.get(perm.content_type.app_label, module_name)
            translated_submodule = translated_submodule_dict.get(perm.content_type.model, submodule_name)

            # Traducción de permisos
            translated_permission = translated_permission_dict.get(perm.name, perm.name)

            # Agrupar permisos
            if translated_module not in grouped_permissions:
                grouped_permissions[translated_module] = {}
            if translated_submodule not in grouped_permissions[translated_module]:
                grouped_permissions[translated_module][translated_submodule] = []
            grouped_permissions[translated_module][translated_submodule].append(translated_permission)

        return grouped_permissions

    def send_permissions_email(self, user, to_email):
        """
        Enviar correo como HTML utilizando EmailMultiAlternatives.
        """
        current_site = Site.objects.get_current()
        current_site.domain = settings.SITE_DOMAIN
        site_protocol = settings.SITE_PROTOCOL

        login_url = f"{site_protocol}://{current_site.domain}/members/login/"
        translated_permissions = self.get_translated_permissions(user)
        groups = user.groups.all()
        context = {
            'user': user,
            'translated_permissions': translated_permissions,
            'groups': groups,
            'login_url': login_url
        }
        subject = 'Actualización de tus permisos de usuario'
        body = render_to_string(self.email_template_name, context)

        # Crear el correo con texto plano
        email_message = EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])

        # Adjuntar la versión HTML
        html_body = render_to_string(self.html_email_template_name, context)
        email_message.attach_alternative(html_body, "text/html")

        # Enviar el correo
        email_message.send()

# viers for finances reports
class FinancesDashboardView(TemplateView):
    """
    Vista para mostrar el panel de control de finanzas.

    Esta vista muestra un panel de control con información financiera, incluyendo los ingresos
    totales y el número total de compras. También filtra las categorías premium.

    Atributos:
    ----------
    template_name : str
        El nombre de la plantilla que se utilizará para renderizar la vista.

    Métodos:
    --------
    get_context_data(**kwargs):
        Obtiene el contexto para la plantilla, incluyendo los ingresos totales, el número total
        de compras y las categorías premium.
    """
    template_name = 'finances/dashboard.html'

    def get_context_data(self, **kwargs):
        """
        Obtiene el contexto para la plantilla, incluyendo los ingresos totales, el número total
        de compras y las categorías premium.

        Args:
        -----
        **kwargs : dict
            Argumentos clave adicionales.

        Returns:
        --------
        dict
            El contexto para la plantilla.
        """
        context = super().get_context_data(**kwargs)

        # Total revenue and purchases
        context['total_revenue'] = Purchase.objects.aggregate(total=Sum('price'))['total']
        context['total_purchases'] = Purchase.objects.count()

        # Filtrar categorías premium
        premium_categories = Category.objects.filter(kind='premium')

        # Obtener ventas por categoría premium, incluso si las ventas son 0
        category_sales_data = premium_categories.annotate(
            total_sales=Coalesce(Sum('purchase__price'), Value(0, output_field=DecimalField()))
        )

        # Preparar los datos para el gráfico de barras
        categories = [category.name for category in category_sales_data]
        sales = [float(category.total_sales) for category in category_sales_data]  # Convertir Decimal a float para serializar

        # Serializar los datos como JSON
        context['categories_json'] = json.dumps(categories)
        context['sales_json'] = json.dumps(sales)

        return context


class FinancesMembersView(TemplateView):
    """
    Vista para mostrar las compras realizadas por los miembros.

    Esta vista muestra una lista de todas las compras realizadas por los miembros,
    incluyendo la categoría y el usuario asociado a cada compra.

    Atributos:
    ----------
    template_name : str
        El nombre de la plantilla que se utilizará para renderizar la vista.

    Métodos:
    --------
    get_context_data(**kwargs):
        Obtiene el contexto para la plantilla, incluyendo todas las compras realizadas por los miembros.
    """
    template_name = 'finances/member.html'

    def get_context_data(self, **kwargs):
        """
        Obtiene el contexto para la plantilla, incluyendo todas las compras realizadas por los miembros.

        Args:
        -----
        **kwargs : dict
            Argumentos clave adicionales.

        Returns:
        --------
        dict
            El contexto para la plantilla.
        """
        context = super().get_context_data(**kwargs)
        context['purchases'] = Purchase.objects.select_related('category', 'user').all()
        return context

class FinancesCategoriesView(TemplateView):
    """
    Vista para mostrar el resumen financiero por categorías.

    Esta vista muestra un resumen financiero agrupado por categorías, incluyendo el total
    de ingresos por cada categoría.

    Atributos:
    ----------
    template_name : str
        El nombre de la plantilla que se utilizará para renderizar la vista.

    Métodos:
    --------
    get_context_data(**kwargs):
        Obtiene el contexto para la plantilla, incluyendo el total de ingresos agrupados por categoría.
    """
    template_name = 'finances/category.html'

    def get_context_data(self, **kwargs):
        """
        Obtiene el contexto para la plantilla, incluyendo el total de ingresos agrupados por categoría.

        Args:
        -----
        **kwargs : dict
            Argumentos clave adicionales.

        Returns:
        --------
        dict
            El contexto para la plantilla.
        """
        context = super().get_context_data(**kwargs)
        
        # Group by category name and sum the price
        context['categories'] = Purchase.objects.values('category__name').annotate(total=models.Sum('price'))
        
        return context