import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerifyTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{six.text_type(user.pk)}{six.text_type(timestamp)}{six.text_type(user.email_verified)}"


email_token = EmailVerifyTokenGenerator()
