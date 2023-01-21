from django.test import TestCase
from posts.models import (Post, Group, User, Comment, Follow)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_follower = User.objects.create_user(username='follower')
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
            author=cls.user,
            text='Тестовый текст',
        )
        cls.follow = Follow.objects.create(
            user=cls.user_follower,
            author=cls.user,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_result = post.text[:15]
        self.assertEqual(expected_result, str(post))
        group = PostModelTest.group
        expected_result = group.title
        self.assertEqual(expected_result, str(group))
        comment = PostModelTest.comment
        expected_result = comment.text[:15]
        self.assertEqual(expected_result, str(comment))
        follow = PostModelTest.follow
        expected_result = ('followers')
        self.assertEqual(expected_result, str(follow))

    def test_models_have_correct_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Слаг группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа поста',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_help_texts = {
            'title': 'Введите название группы',
            'slug': 'Введите короткое название латиницей',
            'description': 'Введите описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)

        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'author': 'Введите описание группы',
            'group': 'Выберите группу (опционально)',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
