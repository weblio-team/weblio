from django.urls import path
from .views import GroupListView, CreateGroupView
from .views import MemberListView, MemberEditView

urlpatterns = [
    path('all', MemberListView.as_view(), name='member-list'),
    path('edit/<int:pk>/', MemberEditView.as_view(), name='member-edit'),
    path('groups/', GroupListView.as_view(), name='group-list'),
    path('groups/create/', CreateGroupView.as_view(), name='group-create'),
]