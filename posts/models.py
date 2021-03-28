from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=200,
        null=False,
        help_text='Дайте короткое название создаваемой группе',
    )
    slug = models.SlugField(
        verbose_name='Адрес для страницы с группой',
        unique=True,
        help_text='Укажите адрес для страницы группы. Используйте только '
        'латиницу, цифры, дефисы и знаки подчёркивания',
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Укажите описание создаваемой группы'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Напишите текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='date published',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Имя пользователя',
        help_text='Выберите пользователя',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Название группы',
        help_text='Выберите группу',
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Напишите текст комментария'
    )
    created = models.DateTimeField(
        verbose_name='date published',
        auto_now_add=True,
    )

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):

    class Meta:
        unique_together = ['user', 'author']

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name="follower"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписант',
        related_name="following"
    )

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
