from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.http.response import Http404, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, get_list_or_404
from . import (
    mixins,
    tokens,
    forms
)
from django_registration.backends.one_step.views import RegistrationView
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
    RedirectURLMixin
)
from django.views.generic import (
    DetailView,
    DeleteView,
    UpdateView,
    RedirectView,
    TemplateView,
    CreateView
)


USER_MODEL = get_user_model()


class ProfileView(LoginRequiredMixin, mixins.EmailVerifiedMixin, DetailView):
    """
    Страница для просмотра профиля авторизованному пользователю.
    """

    template_name = 'account/profile.html'

    def get_object(self, queryset=None):
        return self.request.user


class CustomLoginView(LoginView):
    """
    Страница для авторизации пользователя.
    """

    form_class = forms.AuthorizationForm
    redirect_field_name = 'next'
    redirect_authenticated_user = True
    template_name = 'account/login.html'


class CustomRegistrationView(RegistrationView):
    """
    Страница для регистрации пользователя.
    """

    form_class = forms.RegistrationForm
    redirect_field_name = 'next'
    redirect_authenticated_user = True
    template_name = 'account/registration.html'


class CustomPasswordChangeView(PasswordChangeView):
    """
    Страница для смены пароля пользователя.
    """

    template_name = 'account/password_change.html'


class CustomPasswordResetView(PasswordResetView):
    """
    Страница для восстановления пароля пользователя.
    """

    template_name = 'account/password_reset.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('profile')


class CustomLogoutView(LogoutView):
    """
    Страница для деавторизации пользователя.
    """

    url = reverse_lazy('index')


class EmailVerificationInfoView(
    LoginRequiredMixin,
    mixins.EmailNotVerifiedMixin,
    TemplateView
):
    """
    Страница для просмотра информации об отправлении письма
    Для подтверждения почты пользователя.
    """

    template_name = 'account/email_verification.html'


class EmailVerificationSend(
    LoginRequiredMixin,
    mixins.EmailNotVerifiedMixin,
    RedirectView
):
    """
    Страница для отправки письма подтверждения почты пользователю на его электронный адрес.
    После отправки перенаправляет пользователя на страницу об информации об отправке письма.
    """

    url = reverse_lazy('email_verification')

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        email = user.email
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = tokens.email_token.make_token(user)

        # mailing.email_verify_mail(request=request, uid=uid, token=token, recipient_list=[email])
        self.url = reverse_lazy('email_verification')
        return super().dispatch(request, *args, **kwargs)


class EmailVerificationCheckView(
    RedirectView
):
    """
    Страница для валидации ссылки с письма для подтверждения почты.
    Если ссылка прошла валидацию - перенаправляет пользователя в профиль
    Иначе отображает текстовую ошибку.
    """

    url = reverse_lazy('profile')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        uid = kwargs.get('uid')
        token = kwargs.get('token')

        if not uid:
            return HttpResponseForbidden()

        if not token:
            return HttpResponseForbidden()

        user_pk = force_str(urlsafe_base64_decode(uid))
        user = get_object_or_404(USER_MODEL, pk=user_pk)

        if not user.is_active:
            raise PermissionDenied

        if user.email_verified:
            messages.warning(request, message='Почта данного акканта уже подтверждена!')
            return super().dispatch(request, *args, **kwargs)

        if tokens.email_token.check_token(user, token):
            messages.success(request, message='Ваша почта была успешно подтверждена!')
            user.email_verified = True
            user.save()
            return super().dispatch(request, *args, **kwargs)

        messages.error(request, message='Произошла неизвестная ошибка. Повторите попытку позднее.')
        return redirect('profile')
