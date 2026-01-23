from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from ..models import Post, Comment, UserProfile
from ..forms import RegistrationForm, ProfileForm, UsernameForm, EmailForm, CustomPasswordChangeForm
from django.contrib.auth import update_session_auth_hash


User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:post_list')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # staty konta
    posts_count = Post.objects.filter(author=user, status='published').count()
    comments_count = Comment.objects.filter(user=user, approved=True).count()
    recent_posts = Post.objects.filter(author=user, status='published')[:5]
    
    # ostatnie komenty
    if request.user.is_superuser:
        recent_comments = Comment.objects.filter(user=user).order_by('-created')[:5]
    elif request.user == user:
        recent_comments = Comment.objects.filter(user=user).order_by('-created')[:5]
    else:
        recent_comments = Comment.objects.filter(user=user, approved=True).order_by('-created')[:5]
    
    return render(request, 'blog/profile_detail.html', {
        'profile_user': user,
        'profile': profile,
        'posts_count': posts_count,
        'comments_count': comments_count,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
    })


@login_required
def profile_edit(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        username_form = UsernameForm(request.POST, instance=request.user, user=request.user)
        email_form = EmailForm(request.POST, instance=request.user, user=request.user)
        password_form = CustomPasswordChangeForm(request.POST, user=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        username_updated = False
        email_updated = False
        password_updated = False
        profile_updated = False
        
        # username form
        if 'update_username' in request.POST:
            if username_form.is_valid():
                username_form.save()
                username_updated = True
                messages.success(request, 'Nazwa użytkownika została zaktualizowana.')
                request.user.refresh_from_db()# przeladuj usera po zmianie nazwy
        
        # email form
        if 'update_email' in request.POST:
            if email_form.is_valid():
                email_form.save()
                email_updated = True
                messages.success(request, 'Email został zaktualizowany.')
        
        # password form
        if 'change_password' in request.POST:
            if password_form.is_valid():
                user = request.user
                user.set_password(password_form.cleaned_data['new_password1'])
                user.save()
                update_session_auth_hash(request, user) # przeladuj usera po zmianie nazwy
                password_updated = True
                messages.success(request, 'Hasło zostało zmienione.')
        
        # profile / bio form edit
        if 'update_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                profile_updated = True
                messages.success(request, 'Profil został zaktualizowany.')
        
        if username_updated or email_updated or password_updated or profile_updated:
            return redirect('blog:profile_detail', username=request.user.username)
    else:
        username_form = UsernameForm(instance=request.user, user=request.user)
        email_form = EmailForm(instance=request.user, user=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'blog/profile_edit.html', {
        'username_form': username_form,
        'email_form': email_form,
        'password_form': password_form,
        'profile_form': profile_form,
        'profile': profile,
    })

