# Import all views for compatibility with urls.py
from .posts import post_list, post_detail, post_create, post_edit, post_like_toggle, search
from .comments import comment_approve, comment_reject, comment_like_toggle
from .profiles import register, profile_detail, profile_edit
from .moderation import warning_create, mute_create, moderation_history
from .notifications import notifications_list, notification_mark_read
from .admin import (
    admin_panel, admin_comments, admin_posts, admin_categories, admin_users,
    category_create, category_edit, category_delete,
    admin_tags, tag_create, tag_edit, tag_delete
)
from .utils import is_user_muted, get_active_mute

__all__ = [
    # Posts
    'post_list',
    'post_detail',
    'post_create',
    'post_edit',
    'post_like_toggle',
    'search',
    # Comments
    'comment_approve',
    'comment_reject',
    'comment_like_toggle',
    # Profiles
    'register',
    'profile_detail',
    'profile_edit',
    # Moderation
    'warning_create',
    'mute_create',
    'moderation_history',
    # Notifications
    'notifications_list',
    'notification_mark_read',
    # Admin
    'admin_panel',
    'admin_comments',
    'admin_posts',
    'admin_categories',
    'admin_users',
    'category_create',
    'category_edit',
    'category_delete',
    'admin_tags',
    'tag_create',
    'tag_edit',
    'tag_delete',
    # Utils
    'is_user_muted',
    'get_active_mute',
]

