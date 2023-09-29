# Generated by Django 4.2.5 on 2023-09-28 23:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_customuser_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 28, 23, 38, 3, 329506, tzinfo=datetime.timezone.utc), error_messages={'required': 'Данное поле обязательно для заполнения.'}, help_text='Дата регистрации пользователя.', verbose_name='Дата регистрации'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='date_password_updated',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 28, 23, 38, 3, 329506, tzinfo=datetime.timezone.utc), error_messages={'required': 'Данное поле обязательно для заполнения.'}, help_text='Дата последней смены пароля пользователя.', verbose_name='Дата смены пароля'),
        ),
    ]
