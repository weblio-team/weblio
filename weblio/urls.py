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
    path("ckeditor/", include('ckeditor_uploader.urls')),
    path('ckeditor/upload/', ImageUploadView.as_view(), name='ckeditor_upload'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)