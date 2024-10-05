from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import CustomImageUploadView
from .views import CreateCheckoutSessionView, PaymentSuccessView, PaymentCancelView
from .views import DashboardClapsPostsView, DashboardUpdownsPostsView, DashboardRatePostsView, DashboardPostsView, DashboardClapsCategoriesView, DashboardUpdownsCategoriesView, DashboardRateCategoriesView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .views import CustomPasswordResetView
from .views import FinancesDashboardView, FinancesMembersView, FinancesCategoriesView

urlpatterns = [

    # urls for ckeditor
    path("ckeditor/", include('ckeditor_uploader.urls')),
    path('ckeditor/upload/', CustomImageUploadView.as_view(), name='ckeditor_upload'),

    # urls for stripe
    path('stripe/create-checkout-session/<int:category_id>/', CreateCheckoutSessionView.as_view(), name='stripe_checkout'),
    path('stripe/payment-success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('stripe/payment-cancel/<int:category_id>/', PaymentCancelView.as_view(), name='payment_cancel'),

    # urls for stats of engagement
    path('stats/engagement/dashboard', DashboardPostsView.as_view(), name='engagement_dashboard'),
    path('stats/engagement/posts/views/', DashboardClapsPostsView.as_view(), name='posts_claps'),
    path('stats/engagement/posts/likes/', DashboardUpdownsPostsView.as_view(), name='posts_updowns'),
    path('stats/engagement/posts/stars/', DashboardRatePostsView.as_view(), name='posts_rates'),
    path('stats/engagement/categories/views/', DashboardClapsCategoriesView.as_view(), name='categories_claps'),
    path('stats/engagement/categories/likes/', DashboardUpdownsCategoriesView.as_view(), name='categories_updowns'),
    path('stats/engagement/categories/stars/', DashboardRateCategoriesView.as_view(), name='categories_rates'),

    # urls for stats of finances
    path('stats/finances/dashboard/', FinancesDashboardView.as_view(), name='finances_dashboard'),
    path('stats/finances/members/', FinancesMembersView.as_view(), name='members_finances'),
    path('stats/finances/categories/', FinancesCategoriesView.as_view(), name='categories_finances'),

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