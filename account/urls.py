from django.urls import path
from . import views

urlpatterns = [
    path(
        'login/',
        views.CustomLoginView.as_view(),
        name='login'
    ),
    path(
        'registration/',
        views.CustomRegistrationView.as_view(),
        name='registration'
    ),
    path(
        'logout/',
        views.CustomLogoutView.as_view(),
        name='logout'
    ),
    path(
        'password_reset/',
        views.CustomPasswordResetView.as_view(),
        name='reset_password'
    ),
    path(
        'password_reset/<uidb64>/<token>',
        views.CustomPasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'password_change/',
        views.CustomPasswordChangeView.as_view(),
        name='password_change'
    ),
    path(
        'profile/',
        views.ProfileView.as_view(),
        name='profile'
    ),
]
