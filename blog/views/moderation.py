from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import Warning, Mute, Notification, ModerationHistory

User = get_user_model()


@login_required
def warning_create(request, username):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    target_user = get_object_or_404(User, username=username)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        if reason:
            warning = Warning.objects.create(
                user=target_user,
                admin=request.user,
                reason=reason
            )
            # powiadomienie
            warning_content_type = ContentType.objects.get_for_model(Warning)
            Notification.objects.create(
                user=target_user,
                type='warning',
                content_type=warning_content_type,
                object_id=warning.id
            )
            # dodaj mod history
            ModerationHistory.objects.create(
                user=target_user,
                admin=request.user,
                action_type='warning',
                details=reason
            )
            messages.success(request, f'Ostrzeżenie zostało nadane użytkownikowi {target_user.username}.')
        else:
            messages.error(request, 'Musisz podać powód ostrzeżenia.')
    
    return redirect('blog:profile_detail', username=username)


@login_required
def mute_create(request, username):
    if not request.user.is_superuser:
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    target_user = get_object_or_404(User, username=username)
    
    if request.method == 'POST':
        duration_days = int(request.POST.get('duration_days', 1))
        expires_at = timezone.now() + timezone.timedelta(days=duration_days)
        
        mute = Mute.objects.create(
            user=target_user,
            admin=request.user,
            duration_days=duration_days,
            expires_at=expires_at
        )
        mute_content_type = ContentType.objects.get_for_model(Mute)
        Notification.objects.create(
            user=target_user,
            type='mute',
            content_type=mute_content_type,
            object_id=mute.id
        )
        ModerationHistory.objects.create(
            user=target_user,
            admin=request.user,
            action_type='mute',
            details=f'Mute na {duration_days} dni, wygasa {expires_at.strftime("%Y-%m-%d %H:%M")}'
        )
        messages.success(request, f'Użytkownik {target_user.username} został wyciszony na {duration_days} dni.')
    
    return redirect('blog:profile_detail', username=username)


@login_required
def moderation_history(request, username):
    target_user = get_object_or_404(User, username=username)
    
    if not (request.user == target_user or request.user.is_superuser):
        messages.error(request, 'Brak uprawnień.')
        return redirect('blog:post_list')
    
    history = ModerationHistory.objects.filter(user=target_user)
    
    action_filter = request.GET.get('action_type', '')
    if action_filter:
        history = history.filter(action_type=action_filter)
    
    return render(request, 'blog/moderation_history.html', {
        'profile_user': target_user,
        'history': history,
        'action_filter': action_filter,
    })

