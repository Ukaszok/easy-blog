from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Comment, UserProfile, Post, Category, Tag

User = get_user_model()


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({
            'class': 'form-input'
        })
        self.fields['category'].required = True
        self.fields['category'].empty_label = 'Wybierz kategorię'
        
        self.fields['title'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Tytuł posta (max 50 znaków)',
            'maxlength': '50'
        })
        
        self.fields['body'].widget.attrs.update({
            'class': 'form-textarea',
            'rows': 15,
            'placeholder': 'Treść posta...'
        })
        
        self.fields['tags'].widget.attrs.update({
            'class': 'form-input',
            'size': '10'
        })
        self.fields['tags'].required = False
        self.fields['tags'].queryset = Tag.objects.all().order_by('name')
        self.fields['tags'].help_text = 'Wybierz tagi (przytrzymaj Ctrl aby wybrać wiele)'

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) > 50:
            raise ValidationError('Tytuł nie może być dłuższy niż 50 znaków.')
        return title

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise ValidationError('Kategoria jest wymagana.')
        return category

    class Meta:
        model = Post
        fields = ('category', 'title', 'body', 'tags')


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields.pop('name', None)
        self.fields.pop('email', None)
        # if self._user is not None and self._user.is_authenticated:
        #     # authenticated users don't need to provide name/email
        #     self.fields.pop('name', None)
        #     self.fields.pop('email', None)

    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class RegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')


class UsernameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Nazwa użytkownika'
        })
        self.fields['username'].label = ''

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.user and username != self.user.username:
            if User.objects.filter(username=username).exists():
                raise ValidationError('Ta nazwa użytkownika jest już zajęta.')
        return username

    class Meta:
        model = User
        fields = ('username',)


class EmailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Email'
        })
        self.fields['email'].label = ''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and email != self.user.email:
            if User.objects.filter(email=email).exists():
                raise ValidationError('Ten email jest już zajęty.')
        return email

    class Meta:
        model = User
        fields = ('email',)


class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label='Aktualne hasło',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Aktualne hasło'
        }),
        required=True
    )
    new_password1 = forms.CharField(
        label='Nowe hasło',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nowe hasło'
        }),
        required=True,
        help_text='Hasło musi zawierać co najmniej 8 znaków.'
    )
    new_password2 = forms.CharField(
        label='Potwierdź nowe hasło',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Potwierdź nowe hasło'
        }),
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if self.user and not self.user.check_password(old_password):
            raise ValidationError('Aktualne hasło jest nieprawidłowe.')
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Hasła nie są identyczne.')
        
        # Validate password
        if password2:
            from django.contrib.auth.password_validation import validate_password
            try:
                validate_password(password2, self.user)
            except ValidationError as e:
                raise ValidationError(e.messages)
        
        return password2


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['picture'].widget = forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'custom-file-input',
            'id': 'id_picture'
        })
        self.fields['picture'].required = False
        self.fields['picture'].label = ''
        
        # Customize bio field
        self.fields['bio'].widget = forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-textarea',
            'placeholder': 'Napisz coś o sobie...'
        })
        self.fields['bio'].label = 'Bio'
        self.fields['bio'].required = False

    class Meta:
        model = UserProfile
        fields = ('picture', 'bio')
