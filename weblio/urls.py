from django.contrib import admin
from django.urls import path, include
from members.views import HomeView
from django.conf import settings
from django.conf.urls.static import static
from ckeditor_uploader.views import ImageUploadView
from members.views import Error404View, Error500View, Error403View


# Se configuran las URL de la aplicacion
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
    urlpatterns +=  path('dashboard/views/', HomeView.as_view(), name='posts_claps'), path('dashboard/updowns/', HomeView.as_view(), name='posts_updowns'), path('dashboard/rates/', HomeView.as_view(), name='posts_rates'), path('dashboard/', HomeView.as_view(), name='posts_dashboard'),
else:
    urlpatterns += path("services/", include('services.urls')),


# Se configuran las vistas de error
handler404 = Error404View.as_view()
handler500 = Error500View.as_view()
handler403 = Error403View.as_view()