from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.base import TemplateView

from yatube import settings

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):

    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, settings.POST_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    form = CommentForm()
    context = {"page": page, "paginator": paginator, "form": form, }
    return render(request, 'index.html', context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    group_list = group.posts.all().order_by('-pub_date')
    paginator = Paginator(group_list, settings.POST_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    form = CommentForm()
    context = {
        "group": group,
        "page": page,
        "paginator": paginator,
        "form": form,
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request):

    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new.html', {"form": form})


def profile(request, username):

    user = get_object_or_404(User, username=username)
    users_post = user.posts.all()
    users_post_count = users_post.count()
    current_user = request.user
    form = CommentForm()
    followers = Follow.objects.filter(author__username=username).all()
    followers_count = followers.count()
    following = Follow.objects.filter(user__username=username).all()
    following_count = following.count

    paginator = Paginator(users_post, settings.POST_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        "profile": user,
        "page": page,
        "current_user": current_user,
        "paginator": paginator,
        "count": users_post_count,
        "form": form,
        "followers_count": followers_count,
        "following_count": following_count,
        "following": following,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):

    current_user = request.user
    post = get_object_or_404(Post, id=post_id, author__username=username)
    user = post.author
    users_post_count = user.posts.all().count()
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'profile': user,
        'post': post,
        'count': users_post_count,
        'current_user': current_user,
        'form': form,
        'comments': comments,
    }
    return render(request, 'post.html', context)


# @login_required
def post_edit(request, username, post_id):

    post = get_object_or_404(Post, id=post_id, author__username=username)

    if request.user != post.author:
        return redirect('post', username, post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post
                    )

    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    return render(
        request, "new.html", {"form": form, "post": post})


def add_comment(request, username, post_id):

    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):

    post = get_object_or_404(Post, author__following__user=request.user)
    paginator = Paginator(post, settings.POST_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {"page": page, "paginator": paginator}
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):

    user = request.user
    author = get_object_or_404(User, username=username)
    if author != user:
        Follow.objects.get_or_create(author=author, user=user)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):

    user = request.user
    author = get_object_or_404(User, username=username)
    if author != user:
        Follow.objects.filter(author=author, user=user).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):

    context = {"path": request.path}
    return render(request, "misc/404.html", context, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


class JustStaticPage(TemplateView):

    template_name = 'just_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['just_title'] = 'Очень простая страница'
        context['just_text'] = 'На создание этой страницы у меня ушло 5 минут!'
        return context
