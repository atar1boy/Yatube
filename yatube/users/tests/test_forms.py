from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class UsersCreateFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_users_creates_correctly(self):
        '''Форма корректно создает новых пользователей'''
        expected_count = User.objects.count() + 1
        form_data = {
            'first_name': 'Настя',
            'last_name': 'Нестерова',
            'username': 'anastasus',
            'email': 'anastasus@yandex.ru',
            'password1': 'rnb852ranked',
            'password2': 'rnb852ranked',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), expected_count)
