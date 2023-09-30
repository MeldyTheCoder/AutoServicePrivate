from django.contrib.auth import get_user_model
from django.conf import settings
from _thread import start_new_thread
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string

USER_MODEL = get_user_model()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class Mailing:
    user_model = get_user_model()
    templates_path = settings.BASE_DIR / 'templates/' / 'mailing/'

    @classmethod
    def to_thread(cls, func, *args, **kwargs):
        return start_new_thread(func, *args, **kwargs)

    @classmethod
    def email_verify_mail(cls, request, uid, token, recipient_list: list[str], **kwargs):
        def process():
            title = f"Подтверждение почты"

            user = request.user

            domain = get_current_site(request)

            context = {
                'domain': domain,
                'uid': uid,
                'token': token,
                'user': user,
                **kwargs
            }

            template = cls.templates_path / 'email_verification.html'
            template_raw = render_to_string(template, context=context)

            return send_mail(
                title,
                html_message=template_raw,
                recipient_list=recipient_list,
                message=None,
                from_email=None
            )

        return cls.to_thread(process, ())

    @classmethod
    def authentication_mail(cls, request):
        def process():
            title = f"Безопасность"

            user = request.user
            if not user.is_authenticated:
                return

            from_ip = get_client_ip(request)

            context = {
                'user': user,
                'last_login': user.last_login,
                'from_ip': from_ip
            }

            template = cls.templates_path / 'auth_notification.html'
            template_raw = render_to_string(template, context=context)

            return send_mail(
                title,
                html_message=template_raw,
                recipient_list=[user.email],
                message=None,
                from_email=None
            )

        return cls.to_thread(process, ())


mailing = Mailing
