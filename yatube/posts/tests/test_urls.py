from django.test import Client, TestCase
from posts.models import Post, Group, User
from http import HTTPStatus
from django.core.cache import cache


URL_NAMES = {
    'index': '/',
    'group_list': '/group/{}/',
    'profile': '/profile/{}/',
    'post_detail': '/posts/{}/',
    'post_edit': '/posts/{}/edit/',
    'post_create': '/create/',
    'add_comment': '/posts/{}/comment/',
    'follow_index': '/follow/',
}
REDIRECT_URL = '/auth/login/?next='


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_url_available_to_any_user(self):
        """URL-адрес доступен любому пользователю."""
        group = PostURLTests.group
        user = PostURLTests.user
        post = PostURLTests.post
        url_names = [
            URL_NAMES['index'],
            URL_NAMES['group_list'].format(group.slug),
            URL_NAMES['profile'].format(user.username),
            URL_NAMES['post_detail'].format(post.id),
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_incorrect_url_causes_404(self):
        """Неправильный URL-адрес вызовет ошибку"""
        response = self.guest_client.get('/page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_about_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        group = PostURLTests.group
        user = PostURLTests.user
        post = PostURLTests.post
        templates_url_names = {
            URL_NAMES['index']: 'posts/index.html',
            URL_NAMES['group_list'].format(group.slug): (
                'posts/group_list.html'),
            URL_NAMES['profile'].format(user.username): 'posts/profile.html',
            URL_NAMES['post_detail'].format(post.id): 'posts/post_detail.html',
            URL_NAMES['post_edit'].format(post.id): 'posts/post_create.html',
            URL_NAMES['post_create']: 'posts/post_create.html'
        }
        for address, templates in templates_url_names.items():
            with self.subTest(address=address):
                cache.clear()
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, templates)

    def test_task_list_url_redirect_anonymous_on_login(self):
        """URL-адрес перенаправляет анонимного пользователя."""
        post = PostURLTests.post
        templates_url_names = {
            URL_NAMES['post_create']: '{}/create/'.format(REDIRECT_URL),
            URL_NAMES['post_edit'].format(post.id): (
                '{}/posts/{}/edit/'.format(REDIRECT_URL, post.id)),
            URL_NAMES['add_comment'].format(post.id): (
                '{}/posts/{}/comment/'.format(REDIRECT_URL, post.id)),
            URL_NAMES['follow_index']: '{}/follow/'.format(REDIRECT_URL),
        }
        for address, redirect in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                try:
                    self.assertRedirects(response, redirect)
                except AssertionError:
                    self.assertRedirects(response, redirect, status_code=301)
