from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import CustomImageUploadView
from .views import CreateCheckoutSessionView, PaymentSuccessView, PaymentCancelView
from .views import DashboardClapsPostsView, DashboardUpdownsPostsView, DashboardRatePostsView, DashboardPostsView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .views import CustomPasswordResetView

urlpatterns = [

    # urls for ckeditor
    path("ckeditor/", include('ckeditor_uploader.urls')),
    path('ckeditor/upload/', CustomImageUploadView.as_view(), name='ckeditor_upload'),

    # urls for stripe
    path('stripe/create-checkout-session/<int:category_id>/', CreateCheckoutSessionView.as_view(), name='stripe_checkout'),
    path('stripe/payment-success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('stripe/payment-cancel/<int:category_id>/', PaymentCancelView.as_view(), name='payment_cancel'),

    # urls for dashboard
    path('dashboard/views/', DashboardClapsPostsView.as_view(), name='posts_claps'),
    path('dashboard/updowns/', DashboardUpdownsPostsView.as_view(), name='posts_updowns'),
    path('dashboard/rates/', DashboardRatePostsView.as_view(), name='posts_rates'),
    path('dashboard/', DashboardPostsView.as_view(), name='posts_dashboard'),

    # urls for password reset
    path('password-reset-email/', CustomPasswordResetView.as_view(
        template_name='emails/password-reset/password_reset_form.html',
        email_template_name='emails/password-reset/password_reset_email.html',
        success_url=reverse_lazy('password_reset_done_email')
    ), name='reset_password_email'),
    path('password-reset-sent-email/', auth_views.PasswordResetDoneView.as_view(
        template_name='emails/password-reset/password_reset_done.html'), name='password_reset_done_email'),
    path('password-reset-email/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='emails/password-reset/password_reset_confirm.html',
        success_url=reverse_lazy('member-login')
    ), name='password_reset_confirm_email'),
    path('password-reset-complete-email/', auth_views.PasswordResetCompleteView.as_view(
        template_name='emails/password-reset/password_reset_complete.html'), name='password_reset_complete_email'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)