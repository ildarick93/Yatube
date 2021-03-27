from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Заголовок',
        )

        cls.post = Post.objects.create(
            text='Текст',
            group=cls.group,
            author=User.objects.create(username='Имя пользователя'),
        )

    def test_verbose_name(self):

        field_verboses = {
            'text': 'Текст',
            'group': 'Название группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):

        field_help_texts = {
            'text': 'Напишите текст поста',
            'group': 'Выберите группу',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)

    def test_post_text_str(self):

        self.assertEqual(str(self.post), self.post.text[:15])

    def test_group_title_str(self):

        title = str(self.group)
        self.assertEqual(title, self.group.title)
