from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .forms import CommentForm, PostForm, ProfileEditForm, Profile
from .models import Category, Comment, Post, User
from .utils import filtered_posts

POSTS_ON_PAGE = 10


class PostListView(ListView):
    """Вывод списка постов."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        posts = filtered_posts(True).annotate(
            comment_count=Count('comments')
        ).order_by('pub_date')
        return posts


class PostDetailView(DetailView):
    """Описание поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super(PostDetailView, self).get_object()
        if post.author != self.request.user:
            post = get_object_or_404(
                filtered_posts(),
                pk=self.kwargs['post_id']
            )
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание постов."""

    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostMixin(LoginRequiredMixin):
    """Миксин для постов."""

    model = Post
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostMixin, UpdateView):
    """Изменение постов."""

    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.pk}
        )


class PostDeleteView(PostMixin, DeleteView):
    """Удаление постов."""

    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')


class ProfileListView(ListView):
    """Страница профиля."""

    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/profile.html'

    def get_queryset(self):
        posts = (
            Post.objects.select_related('author')
            .filter(author__username=self.kwargs['username'])
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Изменение профиля."""

    template_name = 'blog/user.html'
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    post_instance = None

    def dispatch(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_instance
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.post_instance.pk}
        )


class CommentMixin(LoginRequiredMixin):
    """Миксин для классов комментариев."""

    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
        )
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(CommentMixin, UpdateView):
    """Изменение комментария."""

    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    """Удаление комментария."""

    pass


def category_posts(request, category_slug):
    """Выбор постов в категории."""
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )
    post_list = filtered_posts(True).filter(
        category__slug=category_slug
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        'category': category,
        "page_obj": page_obj,
    }
    template = 'blog/category.html'
    return render(request, template, context)
