from django.contrib import admin
from .models import Post, Category, Comment, UserProfile, Like, Warning, Mute, Notification, ModerationHistory, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'published')
    list_filter = ('status', 'created', 'published', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ('author',)
    date_hierarchy = 'published'
    ordering = ('status', 'published')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'user', 'created', 'approved')
    list_filter = ('approved', 'created')
    search_fields = ('name', 'email', 'body', 'user__username')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
    approve_comments.short_description = 'Aprove'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'updated')
    search_fields = ('user__username', 'user__email')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id', 'created')
    list_filter = ('content_type', 'created')
    search_fields = ('user__username',)


@admin.register(Warning)
class WarningAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin', 'created')
    list_filter = ('created',)
    search_fields = ('user__username', 'admin__username', 'reason')


@admin.register(Mute)
class MuteAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin', 'duration_days', 'expires_at', 'created')
    list_filter = ('created', 'expires_at')
    search_fields = ('user__username', 'admin__username')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'read', 'created')
    list_filter = ('type', 'read', 'created')
    search_fields = ('user__username',)


@admin.register(ModerationHistory)
class ModerationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin', 'action_type', 'created')
    list_filter = ('action_type', 'created')
    search_fields = ('user__username', 'admin__username', 'details')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
