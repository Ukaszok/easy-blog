from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Comment


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self._user is not None and self._user.is_authenticated:
            # authenticated users don't need to provide name/email
            self.fields.pop('name', None)
            self.fields.pop('email', None)

    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class RegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')
