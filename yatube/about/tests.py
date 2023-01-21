from django.test import Client, TestCase
from http import HTTPStatus
from django.urls import reverse


class AboutTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_url_available_to_any_user(self):
        """URL-адрес доступен любому пользователю."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """URL-адрес использует правильный шаблон"""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_about_url_uses_correct_name(self):
        """Имена URL-адресов корректно указаны"""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
