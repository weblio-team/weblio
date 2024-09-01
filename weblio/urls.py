from django.contrib import admin
from django.urls import path, include
from members.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('members/', include('members.urls')),
    path('posts/posts/', include('posts.urls')),
    path('', HomeView.as_view(), name='home'),
]