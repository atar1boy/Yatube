from django.test import Client, TestCase


class AboutTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_url_uses_correct_template(self):
        """URL-адрес ошибки 404 использует правильный шаблон"""
        response = self.guest_client.get('/wrong_address')
        self.assertTemplateUsed(response, 'core/404.html')
