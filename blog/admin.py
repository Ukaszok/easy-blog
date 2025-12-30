from django.contrib import admin
from .models import Post, Category, Comment


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
