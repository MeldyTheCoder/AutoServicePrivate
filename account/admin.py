from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from . import forms


USER_MODEL = get_user_model()


@admin.register(USER_MODEL)
class CustomUserAdmin(UserAdmin):
    form = forms.CustomUserChangeForm
    add_form = forms.CustomUserCreationForm

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Персональные данные",
            {
                "fields":
                    (
                        "first_name",
                        "last_name",
                        "email"
                    )
            }
        ),
        (
            "Права",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_email_verified",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Важные даты",
            {
                "fields":
                    (
                        "last_login",
                        "date_joined",
                        "date_password_updated"
                    )
            }
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
