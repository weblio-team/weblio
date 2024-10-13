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

        # urls for stats of engagement
        path('stats/engagement/dashboard', HomeView.as_view(), name='engagement_dashboard'),
        path('stats/engagement/posts/views/', HomeView.as_view(), name='posts_claps'),
        path('stats/engagement/posts/likes/', HomeView.as_view(), name='posts_updowns'),
        path('stats/engagement/posts/stars/', HomeView.as_view(), name='posts_rates'),
        path('stats/engagement/categories/views/', HomeView.as_view(), name='categories_claps'),
        path('stats/engagement/categories/likes/', HomeView.as_view(), name='categories_updowns'),
        path('stats/engagement/categories/stars/', HomeView.as_view(), name='categories_rates'),

        # urls for stats of finances
        path('stats/finances/dashboard/', HomeView.as_view(), name='finances_dashboard'),
        path('stats/finances/posts/', HomeView.as_view(), name='members_finances'),
        path('stats/finances/categories/', HomeView.as_view(), name='categories_finances'),

        # urls for member purchase
        path('member-purchase/', HomeView.as_view(), name='member_purchase'),

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