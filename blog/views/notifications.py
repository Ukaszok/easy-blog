from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Notification


@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user)
    
    type_filter = request.GET.get('type', '')
    if type_filter:
        notifications = notifications.filter(type=type_filter)
    
    unread_count = Notification.objects.filter(user=request.user, read=False).count()
    
    return render(request, 'blog/notifications.html', {
        'notifications': notifications,
        'type_filter': type_filter,
        'unread_count': unread_count,
    })


@login_required
def notification_mark_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    messages.success(request, 'Powiadomienie oznaczone jako przeczytane.')
    return redirect('blog:notifications_list')

