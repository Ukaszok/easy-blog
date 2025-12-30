from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Post
from .forms import CommentForm, RegistrationForm


@login_required
def post_list(request):
    posts = Post.objects.filter(status='published')
    return render(request, 'blog/list.html', {'posts': posts})


@login_required
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    comments = post.comments.filter(approved=True)

    if request.method == 'POST':
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
    })


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
