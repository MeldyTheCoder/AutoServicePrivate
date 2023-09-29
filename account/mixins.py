from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class EmailVerifiedMixin(AccessMixin):
    """
    Данный Mixin проверяет, подтвердил ли пользователь свою эл. почту или нет.
    Если не подтвердил - перенаправляет пользователя на страницу подтверждения.
    """

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return self.handle_no_permission()

        if not user.is_email_verified:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        user = self.request.user

        if not user.is_authenticated:
            return super().handle_no_permission()

        return redirect('email_verification')


class EmailNotVerifiedMixin(AccessMixin):
    """
    Данный Mixin проверяет, подтвердил ли пользователь свою эл. почту или нет.
    Если подтвердил - перенаправляет пользователя в профиль.
    """

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return self.handle_no_permission()

        if user.is_email_verified:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        user = self.request.user

        if not user.is_authenticated:
            return super().handle_no_permission()

        return redirect('profile')
