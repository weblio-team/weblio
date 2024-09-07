from django.contrib import admin
from django.urls import path, include
from members.views import HomeView
from django.conf import settings
from django.conf.urls.static import static
from ckeditor_uploader.views import ImageUploadView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('members/', include('members.urls')),
    path('posts/', include('posts.urls')),
    path('', HomeView.as_view(), name='home'),
]

# Se configura la URL de la imagen subida del ckeditor segun el entorno
if settings.DEBUG:
    urlpatterns += path("ckeditor/", include('ckeditor_uploader.urls')),
    urlpatterns += path('ckeditor/upload/', ImageUploadView.as_view(), name='ckeditor_upload'),
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += path("ckeditor/", include('services.urls')),