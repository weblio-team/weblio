from django.urls import path
from .views import GroupListView, CreateGroupView, MemberEditGroupView, MemberEditPermissionView
from .views import MemberListView, MemberJoinView, MemberRegisterView, MemberLoginView, MemberStatusView

urlpatterns = [
    path('all', MemberListView.as_view(), name='member-list'),
    path('edit_group/<int:pk>/', MemberEditGroupView.as_view(), name='member-edit-group'),
    path('edit_permission/<int:pk>/', MemberEditPermissionView.as_view(), name='member-edit-permission'),
    path('status/<int:pk>/', MemberStatusView.as_view(), name='member-status'),
    path('groups/', GroupListView.as_view(), name='group-list'),
    path('groups/create/', CreateGroupView.as_view(), name='group-create'),
    
    path('join/', MemberJoinView.as_view(), name='member-join'),
    path('register/', MemberRegisterView.as_view(), name='member-register'),
    path('login/', MemberLoginView.as_view(), name='member-login'),
]
