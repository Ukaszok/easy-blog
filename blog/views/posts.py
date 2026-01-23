from typing import Any
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.utils.text import slugify
from django.utils import timezone
from ..models import Post, Category, Tag, Like, Comment, Notification
from ..forms import PostForm, CommentForm
from .utils import get_active_mute


@login_required
def post_list(request):
    post_content_type = ContentType.objects.get_for_model(Post)
    
    #pokaz tylko kategorie ktore maja w sobie posty
    categories = Category.objects.annotate(
        post_count=Count('post', filter=Q(post__status='published'))
    ).filter(post_count__gt=0)
    
    categories_with_posts = []
    all_post_ids = []
    for category in categories:
        posts = category.post_set.filter(status='published').annotate(
            comment_count=Count('comments', filter=Q(comments__approved=True))
        )
        all_post_ids.extend([p.id for p in posts])
        categories_with_posts.append({
            'category': category,
            'posts': posts
        })
    
    uncategorized_posts = Post.objects.filter(
        status='published',
        category__isnull=True
    ).annotate(
        comment_count=Count('comments', filter=Q(comments__approved=True))
    )
    all_post_ids.extend([p.id for p in uncategorized_posts])
    
    # polubienia dla wszystkich postow
    like_counts_dict = dict(
        Like.objects.filter(
            content_type=post_content_type,
            object_id__in=all_post_ids
        ).values('object_id').annotate(count=Count('id')).values_list('object_id', 'count')
    )
    
    # dodaj polubienia do postow
    for category_data in categories_with_posts:
        for post in category_data['posts']:
            post.like_count = like_counts_dict.get(post.id, 0)
    
    for post in uncategorized_posts:
        post.like_count = like_counts_dict.get(post.id, 0)
    
    # najpolubiejniejszy post
    hottest_post = None
    if all_post_ids:
        hottest_post_id = max(all_post_ids, key=lambda pid: like_counts_dict.get(pid, 0))
        hottest_post = Post.objects.filter(id=hottest_post_id).first()
        if hottest_post:
            hottest_post.like_count = like_counts_dict.get(hottest_post_id, 0)
            hottest_post.comment_count = hottest_post.comments.filter(approved=True).count()
    
    return render(request, 'blog/list.html', {
        'categories_with_posts': categories_with_posts,
        'uncategorized_posts': uncategorized_posts,
        'hottest_post': hottest_post,
    })


@login_required
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # sprawdź dostęp: posty opublikowane są publiczne, szkice tylko dla autora lub admina
    if post.status == 'draft' and not (request.user == post.author or request.user.is_superuser):
        messages.error(request, 'Ten post nie jest dostępny.')
        return redirect('blog:post_list')
    
    # sprawdź, czy post jest opublikowany dla nieautorów/nieadminów
    if post.status != 'published' and not (request.user == post.author or request.user.is_superuser):
        messages.error(request, 'Ten post nie jest dostępny.')
        return redirect('blog:post_list')
    
    # polubienia dla postu
    post_content_type_for_detail = ContentType.objects.get_for_model(Post)
    post_like_count = Like.objects.filter(
        content_type=post_content_type_for_detail,
        object_id=post.id
    ).count()
    post.like_count = post_like_count
    
    # sprawdź, czy użytkownik polubił post
    post_content_type = ContentType.objects.get_for_model(Post)
    user_has_liked_post = Like.objects.filter(
        user=request.user,
        content_type=post_content_type,
        object_id=post.id
    ).exists()
    
    if request.user.is_superuser:
        comments = post.comments.all()
    else:
        comments = post.comments.filter(
            Q(approved=True) | Q(approved=False, user=request.user)
        )
    
    # opatrz komenty polubieniami i sprawdź, czy użytkownik polubił każdy
    comment_content_type = ContentType.objects.get_for_model(Comment)
    comment_ids = [c.id for c in comments]
    
    # ID polubionych komentarzy użytkownika
    user_liked_comment_ids = set(
        Like.objects.filter(
            user=request.user,
            content_type=comment_content_type,
            object_id__in=comment_ids
        ).values_list('object_id', flat=True)
    )
    
    # polubienia dla wszystkich komentarzy
    like_counts_dict = dict(
        Like.objects.filter(
            content_type=comment_content_type,
            object_id__in=comment_ids
        ).values('object_id').annotate(count=Count('id')).values_list('object_id', 'count')
    )
    
    # dodaj polubienia i user_has_liked do każdego komentarza
    for comment in comments:
        comment.like_count = like_counts_dict.get(comment.id, 0)
        comment.user_has_liked = comment.id in user_liked_comment_ids

    if request.method == 'POST':
        # sprawdź, czy użytkownik jest wyciszony
        active_mute = get_active_mute(request.user)
        if active_mute:
            messages.error(request, f'Jesteś wyciszony do {active_mute.expires_at.strftime("%Y-%m-%d %H:%M")}. Nie możesz publikować komentarzy.')
            return redirect(post.get_absolute_url())
        
        form = CommentForm(request.POST, user=request.user)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            if request.user.is_authenticated:
                comment.user = request.user
                comment.name = request.user.get_full_name() or request.user.username
                comment.email = request.user.email or ''
            comment.save()
            return redirect(post.get_absolute_url())
    else:
        form = CommentForm(user=request.user)

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'user_has_liked_post': user_has_liked_post,
    })


@login_required
def post_create(request):
    # sprawdź, czy użytkownik jest wyciszony
    active_mute = get_active_mute(request.user)
    if active_mute:
        messages.error(request, f'Jesteś wyciszony do {active_mute.expires_at.strftime("%Y-%m-%d %H:%M")}. Nie możesz publikować postów.')
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # generuj slug z tytułu
            base_slug = slugify(post.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            post.slug = slug
            
            # ustaw status na podstawie typu użytkownika
            if request.user.is_superuser:
                post.status = 'published'
                post.published = timezone.now()
                messages.success(request, 'Post został opublikowany.')
            else:
                post.status = 'draft'
                messages.success(request, 'Post został zapisany i czeka na akceptację administratora.')
            
            post.save()
            # zapisz wiele do wielu relacji (tagi)
            form.save_m2m()
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    
    return render(request, 'blog/post_create.html', {
        'form': form,
    })


@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # sprawdź uprawnienia: tylko autor lub admin może edytować
    if not (request.user == post.author or request.user.is_superuser):
        messages.error(request, 'Brak uprawnień do edycji tego posta.')
        return redirect('blog:post_detail', slug=post.slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            
            # zaktualizuj slug, jeśli tytuł zmienił się
            new_slug = slugify(post.title)
            if new_slug != post.slug:
                base_slug = new_slug
                counter = 1
                while Post.objects.filter(slug=new_slug).exclude(pk=post.pk).exists():
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1
                post.slug = new_slug
            
            # jeśli admin publikuje, zaktualizuj status i datę publikacji
            if request.user.is_superuser and 'publish' in request.POST:
                post.status = 'published'
                post.published = timezone.now()
                messages.success(request, 'Post został opublikowany.')
            elif request.user.is_superuser and post.status == 'published':
                # zachowaj status opublikowany, jeśli admin edytuje
                pass
            elif not request.user.is_superuser and post.status == 'draft':
                # zwykły użytkownik zachowuje status szkicu
                post.status = 'draft'
            
            post.save()
            # zapisz wiele do wielu relacji (tagi)
            form.save_m2m()
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/post_edit.html', {
        'form': form,
        'post': post,
    })


@login_required
def post_like_toggle(request, post_id):
    if request.method != 'POST':
        return redirect('blog:post_list')
    
    post = get_object_or_404(Post, id=post_id)
    post_content_type = ContentType.objects.get_for_model(Post)
    
    like, created = Like.objects.get_or_create(
        user=request.user,
        content_type=post_content_type,
        object_id=post.id
    )
    
    if not created:
        # polubienie już istnieje, usuń je (wyłącz)
        like.delete()
        messages.success(request, 'Post odlubiony.')
    else:
        messages.success(request, 'Post polubiony!')
        # utwórz powiadomienie dla właściciela postu, jeśli istnieje i nie jest to samo polubienie
        if post.author != request.user:
            Notification.objects.create(
                user=post.author,
                type='like',
                content_type=post_content_type,
                object_id=post.id
            )
    
    return redirect(post.get_absolute_url())


@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    tag_ids = request.GET.getlist('tags')
    category_id = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'date')
    
    # weź tylko opublikowane
    posts = Post.objects.filter(status='published')
    
    # wyszukaj w tytule i treści postu
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )
    
    # filtrowanie po tagach
    if tag_ids:
        posts = posts.filter(tags__id__in=tag_ids).distinct()
    
    # filtrowanie po kategorii
    if category_id:
        posts = posts.filter(category_id=category_id)
    
    # dodaj liczbe komow do posta
    posts = posts.annotate(
        comment_count=Count('comments', filter=Q(comments__approved=True))
    )
    
    post_ids = list(posts.values_list('id', flat=True))
    
    # polubienia dla wszystkich postów
    post_content_type = ContentType.objects.get_for_model(Post)
    like_counts_dict = {}
    if post_ids:
        like_counts_dict = dict(
            Like.objects.filter(
                content_type=post_content_type,
                object_id__in=post_ids
            ).values('object_id').annotate(count=Count('id')).values_list('object_id', 'count')
        )
    
    # dodaj polubienia do postów
    posts_list = list[Any](posts)
    for post in posts_list:
        post.like_count = like_counts_dict.get(post.id, 0)
    
    # sortowanie wyników
    if sort_by == 'likes':
        posts_list.sort(key=lambda p: (p.like_count, p.published), reverse=True)
    elif sort_by == 'comments':
        posts_list.sort(key=lambda p: (p.comment_count, p.published), reverse=True)
    else:
        posts_list.sort(key=lambda p: p.published, reverse=True)
    
    posts = posts_list
    
    # wszystkie tagi i kategorie dla filtrów
    all_tags = Tag.objects.all().order_by('name')
    all_categories = Category.objects.all().order_by('name')
    
    # szukaj frazy tez w komentarzach
    if query:
        matching_comments = Comment.objects.filter(
            body__icontains=query,
            approved=True
        ).select_related('post')
        
        comment_post_ids = [c.post_id for c in matching_comments if c.post.status == 'published']
        if comment_post_ids:
            comment_posts = Post.objects.filter(
                id__in=comment_post_ids,
                status='published'
            ).annotate(
                comment_count=Count('comments', filter=Q(comments__approved=True))
            )
            
            # zastosuj te same filtry do postów komentarzy
            if tag_ids:
                comment_posts = comment_posts.filter(tags__id__in=tag_ids).distinct()
            if category_id:
                comment_posts = comment_posts.filter(category_id=category_id)
            
            # polubienia dla postów komentarzy
            comment_post_ids_filtered = list(comment_posts.values_list('id', flat=True))
            comment_like_counts_dict = {}
            if comment_post_ids_filtered:
                comment_like_counts_dict = dict(
                    Like.objects.filter(
                        content_type=post_content_type,
                        object_id__in=comment_post_ids_filtered
                    ).values('object_id').annotate(count=Count('id')).values_list('object_id', 'count')
                )
            
            # dodaj polubienia do postów komentarzy
            comment_posts_list = list(comment_posts)
            for post in comment_posts_list:
                post.like_count = comment_like_counts_dict.get(post.id, 0)
            
            # połącz i usuń duplikaty
            existing_post_ids = {p.id for p in posts}
            new_comment_posts = [p for p in comment_posts_list if p.id not in existing_post_ids]
            posts = list(posts) + new_comment_posts
            
                    # ponownie sortuj połączone wyniki
            if sort_by == 'likes':
                posts.sort(key=lambda p: (p.like_count, p.published), reverse=True)
            elif sort_by == 'comments':
                posts.sort(key=lambda p: (p.comment_count, p.published), reverse=True)
            else:
                posts.sort(key=lambda p: p.published, reverse=True)
    
    return render(request, 'blog/search.html', {
        'posts': posts,
        'query': query,
        'selected_tags': [int(tid) for tid in tag_ids] if tag_ids else [],
        'selected_category': int(category_id) if category_id else None,
        'sort_by': sort_by,
        'all_tags': all_tags,
        'all_categories': all_categories,
        'results_count': len(posts) if posts else 0,
    })

