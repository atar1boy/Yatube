from django.test import Client, TestCase
from posts.models import Post, Group, User
from django.urls import reverse
from yatube.settings import POST_AMOUNT


TEST_POSTS = 13
EXPECTED_COUNT = TEST_POSTS - POST_AMOUNT


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        post_list = []
        for i in range(TEST_POSTS):
            post_list.append(Post(
                text=f'Тестовый текст {i}', group=cls.group, author=cls.user))
        cls.post = Post.objects.bulk_create(post_list)

    def setUp(self):
        self.client = Client()

    def test_index_first_page_contains_correct_number_of_posts(self):
        """На первой странице ожидается корректное количество постов"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']), POST_AMOUNT)

    def test_index_second_page_contains_correct_number_of_posts(self):
        """На второй странице ожидается корректное количество постов"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), EXPECTED_COUNT)

    def test_group_posts_first_page_contains_correct_number_of_posts(self):
        """На первой странице ожидается корректное количество постов"""
        group = PaginatorViewsTest.group
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': group.slug}))
        self.assertEqual(
            len(response.context['page_obj']), POST_AMOUNT)

    def test_group_posts_second_page_contains_correct_number_of_posts(self):
        """На второй странице ожидается корректное количество постов"""
        group = PaginatorViewsTest.group
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': group.slug}) + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), EXPECTED_COUNT)

    def test_profile_first_page_contains_correct_number_of_posts(self):
        """На первой странице ожидается корректное количество постов"""
        user = PaginatorViewsTest.user
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': user.username}))
        self.assertEqual(
            len(response.context['page_obj']), POST_AMOUNT)

    def test_profile_second_page_contains_correct_number_of_posts(self):
        """На второй странице ожидается корректное количество постов"""
        user = PaginatorViewsTest.user
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': user.username}) + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), EXPECTED_COUNT)
