from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='username')

        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            text='Текст',
            group=cls.group,
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_url_exists_at_desired_location(self):
        """Cтраница 'url' доступна любому пользователю."""
        url_names = [
            '/',
            f'/group/{self.group.slug}/',
            f'/{self.user.username}/',
            f'/{self.user.username}/{self.post.id}/',
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_private_url_exists_at_desired_location(self):
        """Cтраница 'url' доступна авторизованному пользователю."""
        url_names = [
            '/new/',
            f'/{self.user.username}/{self.post.id}/edit/',
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_edit_pages_by_auth_user_who_is_not_author(self):
        """Создаем пост новым пользователем и проверяем
        возможность внести изменения другим пользователем"""
        test_author = User.objects.create(username='another-user')
        another_post = Post.objects.create(
            text='Текст',
            author=test_author,
        )
        test_url = f'/{test_author.username}/{another_post.id}/edit/'
        response = self.authorized_client.get(test_url)
        self.assertEqual(response.status_code, 302)

    def test_url_redirect_anonymous_on_auth_login(self):
        """Cтраница 'url' перенаправит анонимного пользователя
        на страницу логина."""
        username = self.user.username
        post_id = self.post.id
        url_redirect_names = {
            '/new/': '/auth/login/?next=/new/',
            f'/{username}/{post_id}/edit/': f'/{username}/{post_id}/',
            f'/{username}/follow/': f'/auth/login/?next=/{username}/follow/',
            f'/{username}/unfollow/': f'/auth/login/?next=/{username}/unfollow/',
            f'/{username}/{post_id}/comment/': f'/auth/login/?next=/{username}/{post_id}/comment/',
        }
        for url, redirect in url_redirect_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            '/': 'index.html',
            f'/group/{self.group.slug}/': 'group.html',
            '/new/': 'new.html',
            f'/{self.user.username}/{self.post.id}/edit/': 'new.html'
        }
        for url, template in url_templates_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_unexisted_pages_return_404(self):
        """Несуществующие страницы возвращают ответ 404"""
        urls = [
            '/ildarick97/',
            f'/{self.user.username}/123/edit/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 404)
