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

# Se configuran las URLs de los servicios externos segun el entorno
if settings.DEBUG:
    urlpatterns += [
        
        # URLs for ckeditor (development)
        path("ckeditor/", include('ckeditor_uploader.urls')),
        path('ckeditor/upload/', ImageUploadView.as_view(), name='ckeditor_upload'),

        # URLs for stripe (development)
        path('stripe/create-checkout-session/<int:category_id>/', HomeView.as_view(), name='stripe_checkout'),
        path('stripe/payment-success/', HomeView.as_view(), name='payment_success'),
        path('stripe/payment-cancel/<int:category_id>/', HomeView.as_view(), name='payment_cancel'),

        # URLs for dashboard (development)
        path('dashboard/posts/views/', HomeView.as_view(), name='posts_claps'),
        path('dashboard/posts/likes/', HomeView.as_view(), name='posts_updowns'),
        path('dashboard/posts/stars/', HomeView.as_view(), name='posts_rates'),
        path('dashboard/categories/views/', HomeView.as_view(), name='categories_claps'),
        path('dashboard/categories/likes/', HomeView.as_view(), name='categories_updowns'),
        path('dashboard/categories/stars/', HomeView.as_view(), name='categories_rates'),
        path('dashboard/', HomeView.as_view(), name='posts_dashboard'),

        # URLs for password reset email (development)
        path('members/reset_password/', HomeView.as_view(), name='reset_password_email'),
        path('members/password_reset_done/', HomeView.as_view(), name='password_reset_done_email'),
        path('members/password_reset_confirm/', HomeView.as_view(), name='password_reset_confirm_email'),
        path('members/password_reset_complete/', HomeView.as_view(), name='password_reset_complete_email'),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += [
        path("services/", include('services.urls')),
    ]

# Se configuran las vistas de error
handler404 = Error404View.as_view()
handler500 = Error500View.as_view()
handler403 = Error403View.as_view()