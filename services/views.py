from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

class CustomImageUploadView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
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
