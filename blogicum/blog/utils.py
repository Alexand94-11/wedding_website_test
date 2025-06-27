from django.db.models import Count
from django.utils import timezone

from .models import Post


def filtered_posts(filtering=False):
    """Функция для фильтрации объектов."""
    filtered_posts = Post.objects.select_related(
        'author', 'category'
    )
    if filtering:
        filtered_posts.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
    return filtered_posts
