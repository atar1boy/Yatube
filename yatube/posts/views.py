from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from yatube.settings import POST_AMOUNT, CACHE_PAGE_TIME
from django.views.decorators.cache import cache_page


@cache_page(timeout=CACHE_PAGE_TIME, key_prefix='index_page')
def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, POST_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).all()
    paginator = Paginator(posts, POST_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    user = request.user
    username = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=username).all()
    count = posts.count()
    paginator = Paginator(posts, POST_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = user.is_authenticated and Follow.objects.filter(
        author=username, user=user
    ).exists()
    context = {
        'user': user,
        'username': username,
        'following': following,
        'page_obj': page_obj,
        'count': count
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    count = Post.objects.filter(author=post.author).count()
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm()
    context = {
        'comments': comments,
        'form': form,
        'post': post,
        'count': count,
        'is_edit': post.author == request.user,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_сreate(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    form = PostForm()
    context = {
        'is_edit': False,
        'form': form
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(instance=post)
    context = {
        'post': post,
        'is_edit': post.author == request.user,
        'form': form,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    authors = request.user.follower.values_list('author', flat=True)
    posts = Post.objects.filter(author__id__in=authors)
    paginator = Paginator(posts, POST_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if Follow.objects.filter(user=user, author=author).exists():
        return redirect('posts:profile', username=username)
    if author != user:
        Follow.objects.create(user=user, author=author)
        return redirect(
            'posts:profile',
            username=username
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.get(user=user, author__username=username).delete()
    return redirect('posts:profile', username=username)
