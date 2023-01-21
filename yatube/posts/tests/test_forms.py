import shutil
import tempfile

from django.shortcuts import get_object_or_404
from posts.models import Post, Group, User, Comment
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
NEW_IMAGE = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.extra_user = User.objects.create_user(username='test')
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
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Тестовый текст',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostCreateFormTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_creates_correctly(self):
        '''Форма корректно создает записи в Post'''
        user = PostCreateFormTests.user
        expected_count = Post.objects.count() + 1
        uploaded = SimpleUploadedFile(
            name='image.jpeg',
            content=NEW_IMAGE,
            content_type='image/jpeg'
        )
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': user.username}))
        self.assertEqual(Post.objects.count(), expected_count)

    def test_posts_edites_correctly(self):
        '''Форма корректно изменяет записи в Post'''
        post = PostCreateFormTests.post
        expected_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст 1',
            'group': ''
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        edited_post = get_object_or_404(Post, id=post.id)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post.id}))
        self.assertEqual(Post.objects.count(), expected_count)
        self.assertEqual(form_data['text'], edited_post.text)
        self.assertEqual(None, edited_post.group)

    def test_unauthorized_user_cant_create_posts(self):
        '''Неавторизованный пользователь не может создавать посты'''
        post = PostCreateFormTests.post
        expected_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.guest_client = Client().post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=False
        )
        self.assertRedirects(response, (
            '/auth/login/?next=/posts/{}/edit/'.format(post.id)))
        self.assertEqual(Post.objects.count(), expected_count)

    def test_unauthorized_user_cant_edit_posts(self):
        '''Неавторизованный пользователь не может изменять посты'''
        post = PostCreateFormTests.post
        form_data = {
            'text': 'Тестовый текст 1',
            'group': ''
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, (
            '/auth/login/?next=/posts/{}/edit/'.format(post.id)))
        edited_post = get_object_or_404(Post, id=post.id)
        self.assertNotEqual(form_data['text'], edited_post.text)
        self.assertNotEqual(None, edited_post.group)

    def test_only_author_can_edit_his_posts(self):
        '''Только автор может изменять свои посты'''
        self.authorized_client.force_login(self.extra_user)
        post = PostCreateFormTests.post
        form_data = {
            'text': 'Тестовый текст 1',
            'group': ''
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        edited_post = get_object_or_404(Post, id=post.id)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post.id}))
        self.assertNotEqual(form_data['text'], edited_post.text)
        self.assertNotEqual(None, edited_post.group)

    def test_posts_creates_correctly(self):
        '''Форма корректно создает комментарии'''
        post = PostCreateFormTests.post
        expected_count = Comment.objects.count() + 1
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post.id}))
        self.assertEqual(Comment.objects.count(), expected_count)
