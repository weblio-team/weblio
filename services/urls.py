from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import CustomImageUploadView
from .views import CreateCheckoutSessionView, PaymentSuccessView, PaymentCancelView
from .views import DashboardClapsPostsView, DashboardUpdownsPostsView, DashboardRatePostsView, DashboardPostsView

urlpatterns = [
    path("ckeditor/", include('ckeditor_uploader.urls')),
    path('ckeditor/upload/', CustomImageUploadView.as_view(), name='ckeditor_upload'),
    path('stripe/create-checkout-session/<int:category_id>/', CreateCheckoutSessionView.as_view(), name='stripe_checkout'),
    path('stripe/payment-success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('stripe/payment-cancel/<int:category_id>/', PaymentCancelView.as_view(), name='payment_cancel'),
    path('dashboard/views/', DashboardClapsPostsView.as_view(), name='posts_claps'),
    path('dashboard/updowns/', DashboardUpdownsPostsView.as_view(), name='posts_updowns'),
    path('dashboard/rates/', DashboardRatePostsView.as_view(), name='posts_rates'),
    path('dashboard/', DashboardPostsView.as_view(), name='posts_dashboard'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)