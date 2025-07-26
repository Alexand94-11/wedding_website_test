from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

OPTIMAL_LEN = 25


class Profile(models.Model):
    username = models.CharField('Логин', max_length=150)
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    email = models.EmailField('Электронная почта', blank=True)
    guests = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='Со мной будут',
        help_text='Укажите количество и имена гостей, которые будут с вами.'
    )


class PublishedModel(models.Model):
    """Абстрактная модель. Добавляет флаг is_published и created_at."""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


'''
class Location(PublishedModel):
    """Местоположение."""

    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ('name',)

    def __str__(self):
        return f'Местоположение: {self.name[:OPTIMAL_LEN]}'
'''


class Category(PublishedModel):
    """Тематическая категория."""

    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы'
                  ' латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)

    def __str__(self):
        return (f'Категория: {self.title[:OPTIMAL_LEN]}; '
                f'Описание: {self.description[:OPTIMAL_LEN]}...')


class Post(PublishedModel):
    """Публикация."""

    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts_images',
        blank=True
    )

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ('-pub_date',)

    def __str__(self):
        return (f'Вопрос: {self.title[:OPTIMAL_LEN]}; '
                f'Пользователь: {self.author}')


class Comment(models.Model):
    """Комментарии."""

    text = models.TextField('Текст')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='вопрос'
    )
    created_at = models.DateTimeField(
        'Дата и время создания',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return (f'Комментарий пользователя {self.author}: '
                f'{self.text[:OPTIMAL_LEN]}')
