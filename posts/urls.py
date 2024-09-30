from django.urls import path
from .views import SearchExplorePostView, SearchFeedPostView, SuscriberExplorePostsView, SuscriberFeedPostsView, SuscriberPostDetailView, UpdatePostsStatusView
from .views import CategoriesView, CategoryAddView, CategoryDetailView, CategoryEditView, CategoryDeleteView
from .views import ToEditView, ToEditPostView
from .views import ToPublishView, ToPublishPostView
from .views import MyPostsView, MyPostEditView, MyPostAddView, MyPostDeleteView
from .views import KanbanBoardView
from .views import HistoryView, ReportPostView, ReportedPostsView, TogglePostStatusView
from .views import RelevantPostsView


urlpatterns = [
    
    # urls for category administrators
    path('category/', CategoriesView.as_view(), name='categories'),
    path('category/add/', CategoryAddView.as_view(), name='category_add'),
    path('category/<int:pk>/<str:name>/', CategoryDetailView.as_view(), name='category'),
    path('category/<int:pk>/<str:name>/edit/', CategoryEditView.as_view(), name='category_edit'),
    path('category/<int:pk>/<str:name>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    
    # urls for suscribers
    path('all/search/', SearchExplorePostView.as_view(), name='post_search_explore'),
    path('feed/search/', SearchFeedPostView.as_view(), name='post_search_feed'),
    path('all/', SuscriberExplorePostsView.as_view(), name='posts'),
    path('feed/', SuscriberFeedPostsView.as_view(), name='feed'),
    path('<int:pk>/<slug:category>/<str:month>/<str:year>/<slug:title>/', SuscriberPostDetailView.as_view(), name='post'),
    path('<int:pk>/<slug:category>/<str:month>/<str:year>/<slug:title>/report/', ReportPostView.as_view(), name='report_post'),
    path('incidents/', ReportedPostsView.as_view(), name='incidents'),
    path('toggle-post-status/<int:pk>/', TogglePostStatusView.as_view(), name='toggle_post_status'),  


    # urls for authors
    path('my-posts/', MyPostsView.as_view(), name='my-posts'),
    path('my-posts/<int:pk>/', MyPostEditView.as_view(), name='edit-my-post'),
    path('my-posts/add/', MyPostAddView.as_view(), name='add-my-post'),
    path('my-posts/<int:pk>/delete/', MyPostDeleteView.as_view(), name='delete-my-post'),

    
    # urls for editors
    path('to-edit/', ToEditView.as_view(), name='to-edit'),
    path('to-edit/<int:pk>/', ToEditPostView.as_view(), name='edit-a-post'),
    
    # urls for publishers
    path('to-publish/', ToPublishView.as_view(), name='to-publish'),
    path('to-publish/<int:pk>/', ToPublishPostView.as_view(), name='publish-a-post'),

    # urls for kanban board
    path('kanban-board/', KanbanBoardView.as_view(), name='kanban-board'),
    path('update-posts-status/', UpdatePostsStatusView.as_view(), name='update-posts-status'),

    # urls for history
    path('<int:pk>/history/<int:history_id>/', HistoryView.as_view(), name='history'),

    # urls for relevant posts
    path('relevant-posts/', RelevantPostsView.as_view(), name='relevant-posts'),
]