from django.urls import path, include
from .views import HomeView
from .views import CategoriesView, CategoryAddView, CategoryDetailView, CategoryEditView, CategoryDeleteView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('category/all/', CategoriesView.as_view(), name='categories'),
    path('category/add/', CategoryAddView.as_view(), name='category_add'),
    path('category/<int:pk>/<str:name>/', CategoryDetailView.as_view(), name='category'),
    path('category/<int:pk>/<str:name>/edit/', CategoryEditView.as_view(), name='category_edit'),
    path('category/<int:pk>/<str:name>/delete/', CategoryDeleteView.as_view(), name='category_delete'),

    path("ckeditor5/", include('django_ckeditor_5.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)