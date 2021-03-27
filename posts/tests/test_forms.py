import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user = User.objects.create(username='Имя пользователя')

        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Описание',
        )

        cls.post = Post.objects.create(
            text='Текст',
            group=cls.group,
            author=cls.user,
        )

        cls.form = PostForm()

        cls.count = Post.objects.count()

    @classmethod
    def tearDownClass(cls):

        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает пост."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        form_data = {
            'group': self.group.id,
            'text': 'Текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), self.count + 1)
        self.assertTrue(Post.objects.filter(
            text='Текст',
            group=self.group.id,
            image='posts/small.gif').exists()
        )

    def test_edit_existing_post(self):
        """Валидная форма редактирует пост."""
        form_data = {
            'group': self.group.id,
            'text': 'Изменённый текст',
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                    }),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), self.count)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(
            group=self.group.id,
            text='Изменённый текст',
            author=self.user).exists())
