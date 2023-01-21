import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.conf import settings
from posts.models import Post, Group, User, Comment, Follow
from django.urls import reverse
from django import forms
from django.core.cache import cache


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
NEW_IMAGE = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_follower = User.objects.create_user(username='user_follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.group_extra = Group.objects.create(
            title='Дополнительная тестовая группа',
            slug='test_extra',
            description='Тестовая группа для проверки отсутсвия в ней записи',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=SimpleUploadedFile(
                name='image.jpeg',
                content=NEW_IMAGE,
                content_type='image/jpeg'
            )
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый текст',
        )
        cls.follow = Follow.objects.create(
            user=cls.user_follower,
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostViewsTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_follower = PostViewsTests.user_follower
        self.authorized_client_follower = Client()
        self.authorized_client_follower.force_login(self.user_follower)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        group = PostViewsTests.group
        user = PostViewsTests.user
        post = PostViewsTests.post
        templates_url_names = {
            reverse('posts:index'): ('posts/index.html'),
            reverse('posts:group_list', kwargs={'slug': group.slug}): (
                'posts/group_list.html'),
            reverse('posts:profile', kwargs={'username': user.username}): (
                'posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': post.id}): (
                'posts/post_detail.html'),
            reverse('posts:post_edit', kwargs={'post_id': post.id}): (
                'posts/post_create.html'),
            reverse('posts:post_create'): ('posts/post_create.html'),
            reverse('posts:follow_index'): ('posts/follow.html'),
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                cache.clear()
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        post = PostViewsTests.post
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, post.text)
        self.assertEqual(first_object.author, post.author)
        self.assertEqual(first_object.group, post.group)
        self.assertEqual(first_object.image, post.image)

    def test_follow_index_page_show_correct_context(self):
        """Шаблон follow_index сформирован с правильным контекстом."""
        post = PostViewsTests.post
        self.authorized_client.force_login(self.user_follower)
        response = self.authorized_client_follower.get(reverse(
            'posts:follow_index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, post.text)
        self.assertEqual(first_object.author, post.author)
        self.assertEqual(first_object.group, post.group)
        self.assertEqual(first_object.image, post.image)

    def test_user_can_follow_and_unfollow_authors(self):
        """Пользователи могут подписываться и отписываться"""
        user = PostViewsTests.user
        user_follower = PostViewsTests.user_follower
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': user_follower.username}))
        follow = Follow.objects.filter(
            author=user_follower, user=user
        ).exists()
        self.assertTrue(follow)
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': user_follower.username}))
        unfollow = Follow.objects.filter(
            author=user_follower, user=user
        ).exists()
        self.assertFalse(unfollow)

    def test_follow_index_with_follow_and_unfollow_authors(self):
        post = PostViewsTests.post
        user = PostViewsTests.user
        response = self.authorized_client_follower.get(reverse(
            'posts:follow_index',))
        first_obj = response.context['page_obj'][0]
        self.assertEqual(first_obj, post)
        post = Post.objects.create(
            text='Тест подписок',
            author=user
        )
        response = self.authorized_client_follower.get(reverse(
            'posts:follow_index',))
        first_obj = response.context['page_obj'][0]
        self.assertEqual(first_obj, post)

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        post = PostViewsTests.post
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='test_new_post',
            author=post.author,
        )
        response_old = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        post = PostViewsTests.post
        group = PostViewsTests.group
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': group.slug}))
        first_object = response.context['page_obj'][0]
        group_object = response.context['group']
        self.assertEqual(first_object.text, post.text)
        self.assertEqual(first_object.author, post.author)
        self.assertEqual(first_object.group, post.group)
        self.assertEqual(group_object.title, group.title)
        self.assertEqual(first_object.image, post.image)

    def test_post_object_not_shows_on_incorrect_group_pages(self):
        """Объект post не отображается на страницах неправильных групп"""
        post = PostViewsTests.post
        group_extra = PostViewsTests.group_extra
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': group_extra.slug}))
        group_object = response.context['group']
        self.assertNotEqual(group_object.title, post.group)

    def test_profile_posts_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        post = PostViewsTests.post
        user = PostViewsTests.user
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': user.username}))
        cache.clear()
        post_object = response.context['page_obj'][0]
        count_object = response.context['count']
        EXPECTED_COUNT = 1
        self.assertEqual(post_object.text, post.text)
        self.assertEqual(post_object.author, post.author)
        self.assertEqual(post_object.group, post.group)
        self.assertEqual(post_object.image, post.image)
        self.assertEqual(EXPECTED_COUNT, count_object)

    def test_profile_posts_page_show_correct_posts(self):
        """Шаблон profile сформирован только с постами автора."""
        user = PostViewsTests.user
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': user.username}))
        user_object = response.context['username']
        post_object = response.context['page_obj'][0]
        self.assertEqual(user_object.username, post_object.author.username)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        post = PostViewsTests.post
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': post.id}))
        post_object = response.context['post']
        count_object = response.context['count']
        is_edit_object = response.context['is_edit']
        EXPECTED_COUNT = 1
        self.assertEqual(post_object.text, post.text)
        self.assertEqual(post_object.author, post.author)
        self.assertEqual(post_object.group, post.group)
        self.assertEqual(post_object.image, post.image)
        self.assertEqual(count_object, EXPECTED_COUNT)
        self.assertIsInstance(is_edit_object, bool)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        is_edit_object = response.context['is_edit']
        expected_is_edit_object = False
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(is_edit_object, expected_is_edit_object)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        post = PostViewsTests.post
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': post.id}))
        is_edit_object = response.context['is_edit']
        post_object = response.context['post']
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertIsInstance(is_edit_object, bool)
        self.assertEqual(post_object.id, post.id)
