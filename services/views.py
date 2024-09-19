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