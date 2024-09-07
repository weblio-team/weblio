from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import CustomImageUploadView

urlpatterns = [
    path("/", include('ckeditor_uploader.urls')),
    path('upload/', CustomImageUploadView.as_view(), name='ckeditor_upload'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)