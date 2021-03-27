from django.test import Client, TestCase


class AboutURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_public_url_exists_at_desired_location(self):
        """Cтраница 'url' доступна любому пользователю."""
        url_names = [
            '/about/author/',
            '/about/tech/',
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)
