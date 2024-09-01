from django.urls import path, include
from .views import PostsView, PostDetailView, PostAddView, PostEditView, PostDeleteView, SearchPostView
from .views import CategoriesView, CategoryAddView, CategoryDetailView, CategoryEditView, CategoryDeleteView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('all/', PostsView.as_view(), name='posts'),
    path('add/', PostAddView.as_view(), name='post_add'),
    path('<int:pk>/<slug:category>/<str:month>/<str:year>/<slug:title>/', PostDetailView.as_view(), name='post'),
    path('<int:pk>/<slug:category>/<str:month>/<str:year>/<slug:title>/edit/', PostEditView.as_view(), name='post_edit'),
    path('<int:pk>/<slug:category>/<str:month>/<str:year>/<slug:title>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('search/', SearchPostView.as_view(), name='post_search'),

    path('category/all/', CategoriesView.as_view(), name='categories'),
    path('category/add/', CategoryAddView.as_view(), name='category_add'),
    path('category/<int:pk>/<str:name>/', CategoryDetailView.as_view(), name='category'),
    path('category/<int:pk>/<str:name>/edit/', CategoryEditView.as_view(), name='category_edit'),
    path('category/<int:pk>/<str:name>/delete/', CategoryDeleteView.as_view(), name='category_delete'),

    path("ckeditor5/", include('django_ckeditor_5.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)