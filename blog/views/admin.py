import json
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import Post, Comment, Category, Tag, Notification, ModerationHistory


User = get_user_model()


@login_required
def admin_panel(request):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    pending_comments_count = Comment.objects.filter(approved=False).count()
    draft_posts_count = Post.objects.filter(status='draft').count()
    total_users_count = User.objects.count()
    total_categories_count = Category.objects.count()
    
    return render(request, 'blog/admin_panel.html', {
        'pending_comments_count': pending_comments_count,
        'draft_posts_count': draft_posts_count,
        'total_users_count': total_users_count,
        'total_categories_count': total_categories_count,
    })


@login_required
def admin_comments(request):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    comments = Comment.objects.filter(approved=False)
    
    user_filter = request.GET.get('user', '')
    if user_filter:
        comments = comments.filter(Q(user__username__icontains=user_filter) | Q(name__icontains=user_filter))
    
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        comments = comments.order_by('created')
    else:
        comments = comments.order_by('-created')
    
    if request.method == 'POST':
        comment_ids = request.POST.getlist('comment_ids')
        if comment_ids:
            if 'approve_selected' in request.POST:
                Comment.objects.filter(id__in=comment_ids).update(approved=True)
                messages.success(request, f'Zaakceptowano {len(comment_ids)} komentarzy.')
                return redirect('blog:admin_comments')
    
    if request.method == 'DELETE':        
        data = json.loads(request.body)
        comment_ids = data.get('comment_ids', [])
        if comment_ids:
            comments_to_delete = Comment.objects.filter(id__in=comment_ids)
            comment_content_type = ContentType.objects.get_for_model(Comment)
            
            for comment in comments_to_delete:
                if comment.user:
                    ModerationHistory.objects.create(
                        user=comment.user,
                        admin=request.user,
                        action_type='comment_rejected',
                        content_type=comment_content_type,
                        object_id=comment.id,
                        details='Komentarz został odrzucony'
                    )
            
            deleted_count = comments_to_delete.delete()[0]
            return JsonResponse({'success': True, 'deleted_count': deleted_count})
        return JsonResponse({'success': False, 'error': 'Brak ID komentarzy'}, status=400)
    
    return render(request, 'blog/admin_comments.html', {
        'comments': comments,
        'user_filter': user_filter,
        'sort': sort,
    })


@login_required
def admin_posts(request):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    posts = Post.objects.filter(status='draft')
    
    author_filter = request.GET.get('author', '')
    if author_filter:
        posts = posts.filter(author__username__icontains=author_filter)
    
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        posts = posts.order_by('created')
    else:
        posts = posts.order_by('-created')
    
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        if post_id:
            post = get_object_or_404(Post, id=post_id, status='draft')
            if 'publish' in request.POST:
                post.status = 'published'
                post.published = timezone.now()
                post.save()
                
                post_content_type = ContentType.objects.get_for_model(Post)
                Notification.objects.create(
                    user=post.author,
                    type='post_approved',
                    content_type=post_content_type,
                    object_id=post.id
                )
                ModerationHistory.objects.create(
                    user=post.author,
                    admin=request.user,
                    action_type='post_approved',
                    content_type=post_content_type,
                    object_id=post.id,
                    details=f'Post został opublikowany'
                )
                
                messages.success(request, 'Post został opublikowany.')
            elif 'reject' in request.POST:
                post_author = post.author
                post_content_type = ContentType.objects.get_for_model(Post)
                
                ModerationHistory.objects.create(
                    user=post_author,
                    admin=request.user,
                    action_type='post_rejected',
                    content_type=post_content_type,
                    object_id=post.id,
                    details=f'Post został odrzucony'
                )
                
                post.delete()
                messages.success(request, 'Post został odrzucony.')
            return redirect('blog:admin_posts')
    
    return render(request, 'blog/admin_posts.html', {
        'posts': posts,
        'author_filter': author_filter,
        'sort': sort,
    })


@login_required
def admin_categories(request):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    categories = Category.objects.all().order_by('name')
    
    return render(request, 'blog/admin_categories.html', {
        'categories': categories,
    })


@login_required
def category_create(request):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            slug = slugify(name)
            counter = 1
            base_slug = slug
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            Category.objects.create(name=name, slug=slug)
            messages.success(request, 'Kategoria została utworzona.')
            return redirect('blog:admin_categories')
    
    return render(request, 'blog/category_form.html', {
        'action': 'create'
    })


@login_required
def category_edit(request, category_id):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category.name = name
            category.slug = slugify(name)
            category.save()
            messages.success(request, 'Kategoria została zaktualizowana.')
            return redirect('blog:admin_categories')
    
    return render(request, 'blog/category_form.html', {
        'category': category,
        'action': 'edit'
    })


@login_required
def category_delete(request, category_id):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Kategoria została usunięta.')
        return redirect('blog:admin_categories')
    
    return render(request, 'blog/category_form.html', {
        'category': category,
        'action': 'delete'
    })


@login_required
def admin_users(request):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    users = User.objects.all()
    
    user_filter = request.GET.get('user', '')
    if user_filter:
        users = users.filter(username__icontains=user_filter)
    
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        users = users.order_by('date_joined')
    else:
        users = users.order_by('-date_joined')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            target_user = get_object_or_404(User, id=user_id)
            if target_user != request.user:  # nie dawaj zmienic swojego usera
                if 'toggle_superuser' in request.POST:
                    target_user.is_superuser = not target_user.is_superuser
                    target_user.save()
                    messages.success(request, f'Uprawnienia administratora {"nadane" if target_user.is_superuser else "odebrane"} dla {target_user.username}.')
                elif 'toggle_active' in request.POST:
                    target_user.is_active = not target_user.is_active
                    target_user.save()
                    messages.success(request, f'Konto {target_user.username} zostało {"aktywowane" if target_user.is_active else "deaktywowane"}.')
            else:
                messages.error(request, 'Nie możesz modyfikować własnego konta.')
            return redirect('blog:admin_users')
    
    return render(request, 'blog/admin_users.html', {
        'users': users,
        'user_filter': user_filter,
        'sort': sort,
    })


@login_required
def admin_tags(request):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    tags = Tag.objects.all().order_by('name')
    
    name_filter = request.GET.get('name', '')
    if name_filter:
        tags = tags.filter(name__icontains=name_filter)
    
    return render(request, 'blog/admin_tags.html', {
        'tags': tags,
        'name_filter': name_filter,
    })


@login_required
def tag_create(request):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            slug = slugify(name)
            counter = 1
            base_slug = slug
            while Tag.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            Tag.objects.create(name=name, slug=slug)
            messages.success(request, 'Tag został utworzony.')
            return redirect('blog:admin_tags')
    
    return render(request, 'blog/tag_form.html', {
        'action': 'create'
    })


@login_required
def tag_edit(request, tag_id):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    tag = get_object_or_404(Tag, id=tag_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            tag.name = name
            tag.slug = slugify(name)
            tag.save()
            messages.success(request, 'Tag został zaktualizowany.')
            return redirect('blog:admin_tags')
    
    return render(request, 'blog/tag_form.html', {
        'tag': tag,
        'action': 'edit'
    })


@login_required
def tag_delete(request, tag_id):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    tag = get_object_or_404(Tag, id=tag_id)
    
    if request.method == 'POST':
        tag.delete()
        messages.success(request, 'Tag został usunięty.')
        return redirect('blog:admin_tags')
    
    return render(request, 'blog/tag_form.html', {
        'tag': tag,
        'action': 'delete'
    })

