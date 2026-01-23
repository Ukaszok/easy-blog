from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from ..models import Comment, Like, Notification, ModerationHistory


@login_required
def comment_approve(request, comment_id):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    comment = get_object_or_404(Comment, id=comment_id)
    comment.approved = True
    comment.save()
    messages.success(request, 'Komentarz został zaakceptowany.')
    return redirect(comment.post.get_absolute_url())


@login_required
def comment_reject(request, comment_id):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    comment = get_object_or_404(Comment, id=comment_id)
    post_url = comment.post.get_absolute_url()
    comment_user = comment.user
    
    if comment_user:
        comment_content_type = ContentType.objects.get_for_model(Comment)
        ModerationHistory.objects.create(
            user=comment_user,
            admin=request.user,
            action_type='comment_rejected',
            content_type=comment_content_type,
            object_id=comment.id,
            details=f'Komentarz został odrzucony'
        )
    
    comment.delete()
    messages.success(request, 'Komentarz został odrzucony.')
    return redirect(post_url)


@login_required
def comment_like_toggle(request, comment_id):
    if request.method != 'POST':
        return redirect('blog:post_list')
    
    comment = get_object_or_404(Comment, id=comment_id)
    comment_content_type = ContentType.objects.get_for_model(Comment)
    
    like, created = Like.objects.get_or_create(
        user=request.user,
        content_type=comment_content_type,
        object_id=comment.id
    )
    
    if not created:
        like.delete()
        messages.success(request, 'Komentarz odlubiony.')
    else:
        messages.success(request, 'Komentarz polubiony!')
        if comment.user and comment.user != request.user:
            Notification.objects.create(
                user=comment.user,
                type='like',
                content_type=comment_content_type,
                object_id=comment.id
            )
    
    return redirect(comment.post.get_absolute_url())

