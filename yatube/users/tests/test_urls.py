from django.test import Client, TestCase
from http import HTTPStatus


URL_NAMES = {
    'logout': '/auth/logout/',
    'login': '/auth/login/',
    'signup': '/auth/signup/',
}


class UsersURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_url_available_to_any_user(self):
        """URL-адрес доступен любому пользователю."""
        url_names = [
            URL_NAMES['logout'],
            URL_NAMES['login'],
            URL_NAMES['signup'],
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            URL_NAMES['logout']: 'users/logged_out.html',
            URL_NAMES['login']: 'users/login.html',
            URL_NAMES['signup']: 'users/signup.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
