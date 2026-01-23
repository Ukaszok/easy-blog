from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('search/', views.search, name='search'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='blog:login'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
    path('profile/<str:username>/warning/', views.warning_create, name='warning_create'),
    path('profile/<str:username>/mute/', views.mute_create, name='mute_create'),
    path('profile/<str:username>/moderation-history/', views.moderation_history, name='moderation_history'),
    path('comment/<int:comment_id>/approve/', views.comment_approve, name='comment_approve'),
    path('comment/<int:comment_id>/reject/', views.comment_reject, name='comment_reject'),
    path('post/<int:post_id>/like/', views.post_like_toggle, name='post_like_toggle'),
    path('comment/<int:comment_id>/like/', views.comment_like_toggle, name='comment_like_toggle'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notification/<int:notification_id>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/comments/', views.admin_comments, name='admin_comments'),
    path('admin-panel/posts/', views.admin_posts, name='admin_posts'),
    path('admin-panel/categories/', views.admin_categories, name='admin_categories'),
    path('admin-panel/categories/create/', views.category_create, name='category_create'),
    path('admin-panel/categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('admin-panel/categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    path('admin-panel/tags/', views.admin_tags, name='admin_tags'),
    path('admin-panel/tags/create/', views.tag_create, name='tag_create'),
    path('admin-panel/tags/<int:tag_id>/edit/', views.tag_edit, name='tag_edit'),
    path('admin-panel/tags/<int:tag_id>/delete/', views.tag_delete, name='tag_delete'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
]
