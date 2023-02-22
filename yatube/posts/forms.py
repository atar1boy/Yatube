from django import forms
from .models import Post, Comment
from django.utils.translation import gettext_lazy as _


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': _('Напишите пожалуйста свой пост. '),
            'group': _('Выберите группу (опционально). ')
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
