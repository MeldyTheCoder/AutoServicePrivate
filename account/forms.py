from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    SetPasswordForm
)

from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordResetForm
)
from django_registration.forms import RegistrationFormTermsOfService
from django import forms
from django.contrib.auth import get_user_model
from AutoServiceAdmin.forms import CrispyForm

USER_MODEL = get_user_model()


class CustomPasswordResetForm(CrispyForm, PasswordResetForm):
    """
    Форма для сброса пароля пользователя
    """

    submit_field = 'Отправить'


class CustomSetPasswordForm(CrispyForm, SetPasswordForm):
    """
    Форма для установки пароля пользователя
    """

    submit_field = 'Сменить'


class RegistrationForm(CrispyForm, RegistrationFormTermsOfService):
    """
    Форма для регистрации пользователя.
    """

    error_css_class = 'is-invalid'
    required_css_class = 'required'

    submit_field = 'Зарегистрироваться'

    class Meta:
        model = USER_MODEL
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
            'tos'
        ]


class CustomUserCreationForm(UserCreationForm):
    """
    Форма для создания пользователя для админ-панели
    """

    class Meta(UserCreationForm.Meta):
        model = USER_MODEL

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            USER_MODEL.objects.get(username=username)
        except USER_MODEL.DoesNotExist:
            return username

        raise forms.ValidationError(self.error_messages['duplicate_username'])


class CustomUserChangeForm(UserChangeForm):
    """
    Форма для редактирования пользователя для админ-панели
    """

    class Meta(UserChangeForm.Meta):
        model = USER_MODEL


class AuthorizationForm(CrispyForm, AuthenticationForm):
    """
    Форма для авторизации пользователя.
    """

    submit_field = 'Войти'

    error_css_class = 'is-invalid'
    required_css_class = 'required'

    error_messages = {
        "invalid_login":
            "Пожалуйста, введите корректные данные для входа в аккаунт.",

        "inactive": "Этот аккаунт неактивен.",
    }

    class Meta:
        model = USER_MODEL
        fields = ['username', 'password']


class ProfileForm(CrispyForm, forms.ModelForm):
    """
    Форма для редактирования основной информации профиля пользователя
    """

    submit_field = 'Изменить'

    class Meta:
        model = USER_MODEL
        fields = ['first_name', 'last_name']


class ProfileSecurityForm(CrispyForm, forms.ModelForm):
    """
    Форма редактирования настроек безопасности профиля пользователя.
    (Почта, пароль)
    """

    submit_field = 'Изменить'

    class Meta:
        model = USER_MODEL
        fields = ['email', 'password']


class ChangeEmailForVerificationForm(CrispyForm, forms.ModelForm):
    """
    Форма для смены почты при ее верификации, на случай, если
    Пользователь при регистрации или смены почты укажет неверную почту
    """

    submit_field = 'Изменить'

    class Meta:
        model = USER_MODEL
        fields = ['email']


class CustomPasswordChangeForm(CrispyForm, PasswordChangeForm):
    """
    Форма для смены пароля пользователя
    """

    submit_field = 'Сменить'

    error_css_class = 'is-invalid'
    required_css_class = 'required'

    error_messages = {

    }

    old_password = forms.CharField(
        required=True,
        label='Старый пароль',
        widget=forms.PasswordInput,
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
            ('password_incorrect', 'invalid'): 'Указанный Вами пароль введен неверно.'
        }
    )

    new_password1 = forms.CharField(
        required=True,
        label='Новый пароль',
        widget=forms.PasswordInput,
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
            'invalid': 'Некорректный новый пароль.',
            'password_mismatch': 'Введенные Вами пароли не совпадают.'
        }
    )

    new_password2 = forms.CharField(
        required=True,
        label='Подтверждение нового пароля',
        widget=forms.PasswordInput,
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
            'invalid': 'Некорректный новый пароль.',
            'password_mismatch': 'Введенные Вами пароли не совпадают.'
        }
    )


