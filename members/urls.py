from django.urls import path
from .views import GroupListView, CreateGroupView
from .views import MemberListView, MemberEditView

from .views import MemberListView, MemberJoinView, MemberRegisterView, MemberLoginView, MemberEditView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('all', MemberListView.as_view(), name='member-list'),
    path('edit/<int:pk>/', MemberEditView.as_view(), name='member-edit'),
    path('groups/', GroupListView.as_view(), name='group-list'),
    path('groups/create/', CreateGroupView.as_view(), name='group-create'),
    
    path('join/', MemberJoinView.as_view(), name='member-join'),
    path('register/', MemberRegisterView.as_view(), name='member-register'),
    path('login/', MemberLoginView.as_view(), name='member-login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('password-reset-sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]