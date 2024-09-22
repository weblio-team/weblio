from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from posts.models import Category
from django.http import HttpResponseNotAllowed
from django.contrib import messages
import requests
from django.conf import settings
from django.views.generic import TemplateView
from posts.models import Post

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
    def post(self, request, category_id, *args, **kwargs):
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
        # Si llega una solicitud GET, devolver un 405 (Método no permitido)
        return HttpResponseNotAllowed(['POST'])

# Clase para manejar la confirmación del pago
@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessView(View):
    def get(self, request, *args, **kwargs):
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
    def get(self, request, category_id, *args, **kwargs):
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
    template_name = 'dashboard/claps.html'
    
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
    template_name = 'dashboard/updowns.html'
    
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
    template_name = 'dashboard/rates.html'
    
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