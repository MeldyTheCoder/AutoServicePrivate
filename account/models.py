from django.db import models
from django.conf import settings
from datetime import datetime
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, first_name, last_name, **extra_fields):
        if not username:
            raise ValueError('Имя пользователя должно быть указано.')

        if not email:
            raise ValueError('Эл. почта должна быть указана.')

        if not first_name:
            raise ValueError('Имя нового пользователя должно быть указано.')

        if not first_name:
            raise ValueError('Фамилия нового пользователя должна быть указана.')

        email = self.normalize_email(email)
        username = self.model.normalize_username(username)

        user = self.model(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_email_verified', False)

        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_email_verified', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Супер-пользователь должен иметь is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Супер-пользователь должен иметь is_superuser=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Супер-пользователь должен иметь is_email_verified=True.')

        return self._create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Модель, описывающая сущность пользователя (владельца автосалонов)

    Поле first_name - имя пользователя
    Поле last_name - фамилия пользователя
    Поле is_active - маркер, показывающий является ли пользователь активным.
    Поле is_staff - маркер, показывающий является ли пользователь сотрудником сервиса.
    Поле date_joined - дата регистрации пользователя.
    Поле last_login - дата последней авторизации пользователя.
    Поле email - эл. почта.
    Поле is_superuser - маркер, показывающий является ли пользователь администратором сайта.
    Поле is_email_verified - маркер, показывающий подтверждена ли у пользователя почта.
    """

    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        null=False,
        blank=False,
        help_text='Эл. почта пользователя. Должна быть уникальной',
        error_messages={
            'invalid': 'Неверный формат эл. почты.',
            'unique': 'Данная эл. почта уже зарегистрирована.',
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    first_name = models.CharField(
        max_length=50,
        verbose_name='Имя',
        unique=False,
        null=False,
        blank=False,
        validators=[
            RegexValidator('[А-Я][а-я]+'),
        ],
        help_text='Должно состоять только из символов кириллицы.',
        error_messages={
            'invalid': 'Неверный формат имени. Имя должно состоять только из символов кириллицы.',
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия',
        unique=False,
        null=False,
        blank=False,
        validators=[
            RegexValidator('[А-Я][а-я]+'),
        ],
        help_text='Должно состоять только из символов кириллицы.',
        error_messages={
            'invalid': 'Неверный формат фамилии. Имя должно состоять только из символов кириллицы.',
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    is_superuser = models.BooleanField(
        verbose_name='Права супер-пользователя',
        default=False,
        null=False,
        blank=False,
        help_text='Отметьте, если хотите выдать пользователю права супер-пользователя.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    is_email_verified = models.BooleanField(
        verbose_name='Почта пользователя подтверждена',
        default=False,
        null=False,
        blank=False,
        help_text='Отметьте, если хотите автоматически подтвердить почту пользователя.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    is_active = models.BooleanField(
        verbose_name='Пользователь активен',
        default=True,
        null=False,
        blank=False,
        help_text='Отметьте, если хотите сделать пользователя активным или наоборот.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    is_staff = models.BooleanField(
        verbose_name='Пользователь является сотрудником',
        default=False,
        null=False,
        blank=False,
        help_text='Отметьте, если хотите сделать пользователя рабочим персоналом данного сервиса.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    date_joined = models.DateTimeField(
        verbose_name='Дата регистрации',
        default=timezone.now,
        help_text='Дата регистрации пользователя.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    date_password_updated = models.DateTimeField(
        verbose_name='Дата смены пароля',
        default=timezone.now,
        help_text='Дата последней смены пароля пользователя.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        self.date_password_updated = datetime.now(tz=timezone.get_current_timezone())
        return super().set_password(raw_password)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'auth_user'


class EmailNotifications(models.Model):
    """
    Модель, описывающая сущность истории отправки писем пользователю.
    Нужна для контроля паузы во времени отправки писем пользователям.
    """

    class EmailNotificationsTypes(models.TextChoices):
        EMAIL_CONFIRMATION = 'email_verification', 'Подтверждение почты'
        PASSWORD_RESET = 'password_reset', 'Сброс пароля'
        LOGIN_NOTIFICATION = 'login_notification', 'Уведомление о входе в аккаунт'

    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        verbose_name='Кому',
        help_text='Укажите, кому было отправлено письмо.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    send_type = models.CharField(
        choices=EmailNotificationsTypes.choices,
        default=EmailNotificationsTypes.LOGIN_NOTIFICATION,
        max_length=50,
        null=False,
        blank=False,
        verbose_name='Тип отправления',
        help_text='Укажите, по какой причине было отправлено письмо пользователю.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    send_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        null=False,
        blank=False,
        verbose_name='Дата отправки',
        help_text='Укажите, когда было отправлено письмо.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    def __str__(self):
        return self.send_type

    class Meta:
        verbose_name = 'Почтовое отправление'
        verbose_name_plural = 'Почтовые отправления'

