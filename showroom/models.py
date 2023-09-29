import random

from django.db import models
from autoslug import AutoSlugField
from datetime import datetime, timedelta
from django.apps import apps
from django.utils.timezone import (
    get_current_timezone
)
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


def random_slug_number():
    return random.randint(10000, 99999)


class StatisticsQuerySet(models.QuerySet):
    """
    Описание
    """

    def statistics(self, verbose_names=False):
        statistics_filter_fields = self.model.statistics_filter_fields
        statistics_fields = self.model.statistics_fields
        statistics_fields_verbose_names = self.model.statistics_fields_verbose_names

        queryset = self.filter()

        if statistics_fields and isinstance(statistics_fields, dict):
            statistics = queryset.aggregate(
                count=models.Count('pk'),
                **statistics_fields
            )

        else:
            statistics = queryset.aggregate(
                count=models.Count('pk')
            )

        if verbose_names and statistics_fields_verbose_names:
            new_dict = {}
            for key, val in statistics.items():
                verbose_key = statistics_fields_verbose_names.get(key) or key
                new_dict[verbose_key] = val
            return new_dict

        return statistics


class StatisticsManager(models.Manager):
    """
    Менеджер для ведения статистики по другим моделям
    """

    def get_queryset(self):
        return StatisticsQuerySet(self.model, using=self._db)

    def statistics(self, verbose_names=False):
        return self.get_queryset().statistics(verbose_names)


class AbstractStatisticsModel(models.Model):
    """
    Абстрактная модель для ведения статистики по другим моделям
    """

    statistics_filter_fields = ['date_created']
    statistics_fields = None
    statistics_parent = False
    statistics_fields_verbose_names = None

    date_created = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False,
        editable=False,
        verbose_name='Дата создания',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    date_modified = models.DateTimeField(
        auto_now=True,
        blank=False,
        null=False,
        editable=False,
        verbose_name='Дата последнего редактирования',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    objects = StatisticsManager()

    class Meta:
        abstract = True

    @classmethod
    def statistic_models(cls):
        return [subclass for subclass in cls.__subclasses__() if not subclass.statistics_parent]

    @property
    def is_new(self):
        date_value = self.date_created.value_from_object(self)
        return (date_value + timedelta(days=7)) >= datetime.now(tz=get_current_timezone())

    @property
    def time_exists(self):
        date_value = self.date_created.value_from_object(self)
        return datetime.now(tz=get_current_timezone()) - date_value

    def statistics(self, verbose_names=False):
        queryset = self.objects.filter(pk=self.pk)

        if self.statistics_fields and isinstance(self.statistics_fields, dict):
            statistics = queryset.aggregate(
                count=models.Count('pk'),
                **self.statistics_fields
            )

        else:
            statistics = queryset.aggregate(
                count=models.Count('pk')
            )

        if verbose_names and self.statistics_fields_verbose_names:
            new_dict = {}
            for key, val in statistics.items():
                verbose_key = self.statistics_fields_verbose_names.get(key) or key
                new_dict[verbose_key] = val
            return new_dict

        return statistics


class Showroom(AbstractStatisticsModel):
    """
    Модель, описывающая сущность автосалона

    Поле title - название автосалона.
    Поле phone_number - номер телефона автосалона.
    Поле is_verified - маркер, показывающий является ли автосалон верифицированным.
    Поле owner - владелец автосалона (внешний ключ)
    """

    related_name = 'showrooms'

    statistics_parent = True

    statistics_fields_verbose_names = {
        'sales_count': 'Кол-во продаж',
        'sales_products_count': 'Кол-во разных проданных товаров',

        'sales_products_price_avg': 'Средняя цена продаваемого товара',
        'sales_products_price_sum': 'Сумма проданного товара',
        'sales_products_price_min': 'Минимальная цена проданного товара',
        'sales_products_price_max': 'Максимальная цена проданного товара',

        'sales_products_quantity_avg': 'Среднее кол-во единиц продаваемого товара за раз',
        'sales_products_quantity_sum': 'Суммарное кол-во единиц проданного товара',
        'sales_products_quantity_min': 'Минимальное кол-во единиц проданного товара за раз',
        'sales_products_quantity_max': 'Максимальное кол-во единиц проданного товара за раз'

    }

    statistics_fields = {
        # Подсчет кол-ва аттрибутов
        'sales_count': models.ExpressionWrapper(
            models.Count('sales'),
            output_field=models.IntegerField()
        ),
        'sales_products_count': models.ExpressionWrapper(
            models.Count('sales__sold_products'),
            output_field=models.IntegerField()
        ),

        # Статистика по цене проданного товара
        'sales_products_price_avg': models.ExpressionWrapper(
            models.Avg('sales__sold_products__sale_price'),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'sales_products_price_sum': models.ExpressionWrapper(
            models.Sum('sales__sold_products__sale_price'),
            output_field=models.IntegerField()
        ),
        'sales_products_price_min': models.ExpressionWrapper(
            models.Min('sales__sold_products__sale_price'),
            output_field=models.IntegerField()
        ),
        'sales_products_price_max': models.ExpressionWrapper(
            models.Max('sales__sold_products__sale_price'),
            output_field=models.IntegerField()
        ),

        # Статистика по кол-ву проданного товара
        'sales_products_quantity_avg': models.ExpressionWrapper(
            models.Avg('sales__sold_products__quantity'),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'sales_products_quantity_sum': models.ExpressionWrapper(
            models.Sum('sales__sold_products__quantity'),
            output_field=models.IntegerField()
        ),
        'sales_products_quantity_min': models.ExpressionWrapper(
            models.Min('sales__sold_products__quantity'),
            output_field=models.IntegerField()
        ),
        'sales_products_quantity_max': models.ExpressionWrapper(
            models.Max('sales__sold_products__quantity'),
            output_field=models.IntegerField()
        ),

        # Статистика по выручке
        'sales_profit_avg': models.ExpressionWrapper(
            models.Avg(
                (
                    models.F('sold_products__product__supplied_products__supply_price')
                    - models.F('sold_products__sale_price')
                ) * models.F('sold_products__quantity')
            ),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'sales_profit_sum': models.ExpressionWrapper(
            models.Sum(
                (
                        models.F('sold_products__product__supplied_products__supply_price')
                        - models.F('sold_products__sale_price')
                ) * models.F('sold_products__quantity')
            ),
            output_field=models.IntegerField()
        ),
        'sales_profit_max': models.ExpressionWrapper(
            models.Max(
                (
                        models.F('sold_products__product__supplied_products__supply_price')
                        - models.F('sold_products__sale_price')
                ) * models.F('sold_products__quantity')
            ),
            output_field=models.IntegerField()
        ),
        'sales_profit_min': models.ExpressionWrapper(
            models.Min(
                (
                        models.F('sold_products__product__supplied_products__supply_price')
                        - models.F('sold_products__sale_price')
                ) * models.F('sold_products__quantity')
            ),
            output_field=models.IntegerField()
        )
    }

    title = models.CharField(
        verbose_name='Название',
        max_length=100,
        null=False,
        blank=False,
        help_text='Название автосалона.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    phone_number = PhoneNumberField(
        blank=False,
        null=False,
        verbose_name='Номер телефона',
        help_text='Номер телефона для связи с автосалоном.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    slug = AutoSlugField(
        null=False,
        blank=False,
        unique=True,
        editable=False,
        populate_from=lambda instance: f"автосалон-{instance.title}-{random_slug_number()}",
        unique_with=[
          'date_created'
        ],
        verbose_name='Ссылка на объект',
        help_text='Ссылка на объект генерируется автоматически. Используется для адресации в URL-адресах.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    owner = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name=related_name,
        verbose_name='Владелец',
        help_text='Владелец автосалона.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False,
        editable=False,
        verbose_name='Дата создания',
        help_text='Дата создания автосалона.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Автосалон'
        verbose_name_plural = 'Автосалоны'


class Employee(AbstractStatisticsModel):
    """
    Модель, описывающая сущность сотрудника

    Поле first_name - имя сотрудника
    Поле last_name - фамилия сотрудника
    Поле surname - отчество сотрудника
    Поле phone_number - номер телефона сотрудника
    Поле showroom - автосалон, к которому привязан объект (внешний ключ).
    Поле date_joined - дата добавления сотрудника в список сотрудников.
    Поле is_restricted - маркер, указывающий, уволен ли сотрудник или нет.
    """

    related_name = 'employees'

    statistics_fields_verbose_names = {
        'sales_count': 'Кол-во продаж',
        'sales_products_count': 'Кол-во разных проданных товаров',

        'sales_products_price_avg': 'Средняя цена проданного товара',
        'sales_products_price_sum': 'Сумма проданного товара',
        'sales_products_price_min': 'Минимальная цена проданного товара',
        'sales_products_price_max': 'Максимальная цена проданного товара',

        'sales_products_quantity_avg': 'Среднее кол-во единиц проданного товара за раз',
        'sales_products_quantity_sum': 'Суммарное кол-во единиц проданного товара',
        'sales_products_quantity_min': 'Минимальное кол-во единиц проданного товара за раз',
        'sales_products_quantity_max': 'Максимальное кол-во единиц проданного товара за раз'

    }

    statistics_fields = {
        # Подсчет кол-ва аттрибутов
        'sales_count': models.ExpressionWrapper(
            models.Count('sales'),
            output_field=models.IntegerField()
        ),
        'sales_products_count': models.ExpressionWrapper(
            models.Count('sales__sold_products'),
            output_field=models.IntegerField()
        ),

        # Статистика по цене проданного товара
        'sales_products_price_avg': models.ExpressionWrapper(
            models.Avg('sales__sold_products__sale_price'),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'sales_products_price_sum': models.ExpressionWrapper(
            models.Sum('sales__sold_products__sale_price'),
            output_field=models.IntegerField()
        ),
        'sales_products_price_min': models.ExpressionWrapper(
            models.Min('sales__sold_products__sale_price'),
            output_field=models.IntegerField()
        ),
        'sales_products_price_max': models.ExpressionWrapper(
            models.Max('sales__sold_products__sale_price'),
            output_field=models.IntegerField()
        ),

        # Статистика по кол-ву проданного товара
        'sales_products_quantity_avg': models.ExpressionWrapper(
            models.Avg('sales__sold_products__quantity'),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'sales_products_quantity_sum': models.ExpressionWrapper(
            models.Sum('sales__sold_products__quantity'),
            output_field=models.IntegerField()
        ),
        'sales_products_quantity_min': models.ExpressionWrapper(
            models.Min('sales__sold_products__quantity'),
            output_field=models.IntegerField()
        ),
        'sales_products_quantity_max': models.ExpressionWrapper(
            models.Max('sales__sold_products__quantity'),
            output_field=models.IntegerField()
        ),

        # Статистика по выручке
        'sales_profit_avg': models.ExpressionWrapper(
            models.Avg(
                (
                    models.F('sold_products__product__supplied_products__supply_price')
                    - models.F('sold_products__sale_price')
                ) * models.F('sold_products__quantity')
            ),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'sales_profit_sum': models.ExpressionWrapper(
            models.Sum(
                (
                        models.F('sold_products__product__supplied_products__supply_price')
                        - models.F('sold_products__sale_price')
                ) * models.F('sold_products__quantity')
            ),
            output_field=models.IntegerField()
        ),
        'sales_profit_max': models.ExpressionWrapper(
            models.Max(
                (
                        models.F('sold_products__product__supplied_products__supply_price')
                        - models.F('sold_products__sale_price')
                ) * models.F('sold_products__quantity')
            ),
            output_field=models.IntegerField()
        ),
        'sales_profit_min': models.ExpressionWrapper(
            models.Min(
                (
                        models.F('sold_products__product__supplied_products__supply_price')
                        - models.F('sold_products__sale_price')
                ) * models.F('sold_products__quantity')
            ),
            output_field=models.IntegerField()
        )
    }

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=30,
        null=False,
        blank=False,
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=30,
        null=False,
        blank=False,
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    surname = models.CharField(
        verbose_name='Отчество',
        max_length=30,
        null=False,
        blank=False,
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    phone_number = PhoneNumberField(
        blank=False,
        null=False,
        verbose_name='Номер телефона',
        help_text='Номер телефона сотрудника.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    showroom = models.ForeignKey(
        'showroom.Showroom',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name=related_name,
        verbose_name='Автосалон',
        help_text='Укажите автосалон, к которому должен быть привязан данный сотрудник.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
        }
    )

    slug = AutoSlugField(
        null=False,
        blank=False,
        unique=True,
        editable=False,
        populate_from=lambda instance: f"сотрудник-{instance.first_name}-{instance.last_name}-{instance.surname}-{random_slug_number()}",
        unique_with=[
            'last_name',
            'date_created'
        ],
        verbose_name='Ссылка на объект',
        help_text='Ссылка на объект генерируется автоматически. Используется для адресации в URL-адресах.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    date_created = models.DateTimeField(
        verbose_name='дата найма',
        null=False,
        blank=False,
        auto_now_add=True,
        help_text='Укажите, когда был нанят данный сотрудник.',
        editable=False,
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    is_restricted = models.BooleanField(
        verbose_name='Сотрудник уволен',
        null=False,
        blank=False,
        default=False,
        help_text='Отметьте, если сотрудник был уволен.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'


class ProductCategory(AbstractStatisticsModel):
    """
    Модель, описывающая сущность категории товара

    Поле name - название категории.
    Поле slug - ссылка-идентификатор на объект.
    Поле date_created - дата создания категории.
    """

    related_name = 'product_categories'

    statistics_fields_verbose_names = {
        'product_count': 'Кол-во товаров всего',
        'sales_count': 'Кол-во проданных товаров',

        'sales_price_avg': 'Средняя цена заказа',
        'sales_price_sum': 'Суммарная стоимость всех заказов',
        'sales_price_min': 'Минимальная цена заказа',
        'sales_price_max': 'Максимальная цена заказа',

        'sales_quantity_avg': 'Среднее кол-во единиц заказываемого товара за раз',
        'sales_quantity_sum': 'Кол-во единиц заказанного товара всего',
        'sales_quantity_min': 'Минимальное кол-во единиц заказываемого товара за раз',
        'sales_quantity_max': 'Максимальное кол-во единиц заказываемого товара за раз',

        'sales_profit_avg': 'Средняя выручка с продаваемого товара',
        'sales_profit_sum': 'Суммарная выручка с продаваемого товара',
        'sales_profit_min': 'Средняя выручка с продаваемого товара',
        'sales_profit_max': 'Средняя выручка с продаваемого товара',
    }

    statistics_fields = {
        'products_count': models.ExpressionWrapper(
            models.Count('products'),
            output_field=models.IntegerField()
        ),
        'sales_count': models.ExpressionWrapper(
            models.Count('products__sold_products'),
            output_field=models.IntegerField()
        ),

        # Статистика по цене продаваемого товара
        'sales_price_sum': models.ExpressionWrapper(
            models.Sum('products__sold_products__sale_price'),
            output_field=models.IntegerField()
        ),
        'sales_price_avg': models.ExpressionWrapper(
            models.Avg('products__sold_products__sale_price'),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'sales_price_min': models.ExpressionWrapper(
            models.Min('products__sold_products__sale_price'),
            output_field=models.IntegerField()
        ),
        'sales_price_max': models.ExpressionWrapper(
            models.Max('products__sold_products__sale_price'),
            output_field=models.IntegerField()
        ),

        # Статистика по кол-ву продаваемого товара
        'sales_quantity_avg': models.ExpressionWrapper(
            models.Avg('products__sold_products__quantity'),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'sales_quantity_sum': models.ExpressionWrapper(
            models.Sum('products__sold_products__quantity'),
            output_field=models.IntegerField()
        ),
        'sales_quantity_min': models.ExpressionWrapper(
            models.Min('products__sold_products__quantity'),
            output_field=models.IntegerField()
        ),
        'sales_quantity_max': models.ExpressionWrapper(
            models.Max('products__sold_products__quantity'),
            output_field=models.IntegerField()
        ),

        # Статистика по выручке
        'sales_profit_avg': models.ExpressionWrapper(
            models.Avg(
                (
                    models.F('products__supplied_products__supply_price')
                    - models.F('products__sold_products__sale_price')
                ) * models.F('products__sold_products__quantity')
            ),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'sales_profit_sum': models.ExpressionWrapper(
            models.Sum(
                (
                        models.F('products__supplied_products__supply_price')
                        - models.F('products__sold_products__sale_price')
                ) * models.F('products__sold_products__quantity')
            ),
            output_field=models.IntegerField()
        ),
        'sales_profit_max': models.ExpressionWrapper(
            models.Max(
                (
                        models.F('products__supplied_products__supply_price')
                        - models.F('products__sold_products__sale_price')
                ) * models.F('products__sold_products__quantity')
            ),
            output_field=models.IntegerField()
        ),
        'sales_profit_min': models.ExpressionWrapper(
            models.Min(
                (
                        models.F('products__supplied_products__supply_price')
                        - models.F('products__sold_products__sale_price')
                ) * models.F('products__sold_products__quantity')
            ),
            output_field=models.IntegerField()
        )
    }

    name = models.CharField(
        max_length=70,
        null=False,
        blank=False,
        unique=True,
        verbose_name='Название',
        help_text='Название категории. Должно быть уникальным.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
            'unique': 'Название категории должно быть уникальным. Данная категория уже существует.'
        }
    )

    slug = AutoSlugField(
        null=False,
        blank=False,
        unique=True,
        editable=False,
        populate_from=lambda instance: f"категория-{instance.name}-{random_slug_number()}",
        unique_with=[
            'date_created'
        ],
        verbose_name='Ссылка на объект',
        help_text='Ссылка на объект генерируется автоматически. Используется для адресации в URL-адресах.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    showroom = models.ForeignKey(
        'showroom.Showroom',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name=related_name,
        verbose_name='Автосалон',
        help_text='Укажите автосалон, к которому должна быть привязана категория товаров.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
        }
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        editable=False,
        verbose_name='Дата создания',
        help_text='Дата создания автосалона.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория товаров'
        verbose_name_plural = 'Категории товаров'


class Product(AbstractStatisticsModel):
    """
    Модель, описывающая сущность товара

    Поле title - название товара.
    Поле description - описание товара.
    Поле price - цена товара.
    Поле slug - ссылка-идентификатор на объект.
    Поле category - категория товара (внешний ключ).
    Поле showroom - автосалон, к которому привязан объект (внешний ключ).
    Поле date_created - дата создания категории.
    """

    related_name = 'products'

    statistics_fields_verbose_names = {
        'product_count': 'Кол-во товаров всего',
        'sales_count': 'Кол-во проданных товаров',

        'sales_price_avg': 'Средняя цена заказа',
        'sales_price_sum': 'Суммарная стоимость всех заказов',
        'sales_price_min': 'Минимальная цена заказа',
        'sales_price_max': 'Максимальная цена заказа',

        'sales_quantity_avg': 'Среднее кол-во заказываемого товара за раз',
        'sales_quantity_sum': 'Суммарное кол-во заказанного товара',
        'sales_quantity_min': 'Минимальное кол-во заказанного товара за раз',
        'sales_quantity_max': 'Максимальное кол-во заказанного товара за раз',

        'sales_profit_avg': 'Средняя выручка с продаваемого товара',
        'sales_profit_sum': 'Суммарная выручка с продаваемого товара',
        'sales_profit_min': 'Средняя выручка с продаваемого товара',
        'sales_profit_max': 'Средняя выручка с продаваемого товара',
    }

    statistics_fields = {
        'product_count': models.ExpressionWrapper(
            models.Count('pk'),
            output_field=models.IntegerField()
        ),
        'sales_count': models.ExpressionWrapper(
            models.Count('sold_products'),
            output_field=models.IntegerField()
        ),

        # Статистика по цене продаваемого товара
        'sales_price_avg': models.ExpressionWrapper(
            models.Avg('sold_products__sale_price'),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'sales_price_sum': models.ExpressionWrapper(
            models.Sum('sold_products__sale_price'),
            output_field=models.IntegerField()
        ),
        'sales_price_min': models.ExpressionWrapper(
            models.Min('sold_products__sale_price'),
            output_field=models.IntegerField()
        ),
        'sales_price_max': models.ExpressionWrapper(
            models.Max('sold_products__sale_price'),
            output_field=models.IntegerField()
        ),

        # Статистика по кол-ву проданного товара
        'sales_quantity_avg': models.ExpressionWrapper(
            models.Avg('sold_products__quantity'),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'sales_quantity_sum': models.ExpressionWrapper(
            models.Sum('sold_products__quantity'),
            output_field=models.IntegerField()
        ),
        'sales_quantity_min': models.ExpressionWrapper(
            models.Min('products__sold_products__quantity'),
            output_field=models.IntegerField()
        ),
        'sales_quantity_max': models.ExpressionWrapper(
            models.Max('products__sold_products__quantity'),
            output_field=models.IntegerField()
        ),

        # Статистика по выручке
        'sales_profit_avg': models.ExpressionWrapper(
            models.Avg(
                (
                    models.F('supplied_products__supply_price')
                    - models.F('sold_products__sale_price')
                ) * models.F('sold_products__quantity')
            ),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'sales_profit_sum': models.ExpressionWrapper(
            models.Sum(
                (
                        models.F('supplied_products__supply_price')
                        - models.F('sold_products__sale_price')
                ) * models.F('sold_products__quantity')
            ),
            output_field=models.IntegerField()
        ),
        'sales_profit_max': models.ExpressionWrapper(
            models.Max(
                (
                        models.F('supplied_products__supply_price')
                        - models.F('sold_products__sale_price')
                ) * models.F('sold_products__quantity')
            ),
            output_field=models.IntegerField()
        ),
        'sales_profit_min': models.ExpressionWrapper(
            models.Min(
                (
                        models.F('supplied_products__supply_price')
                        - models.F('sold_products__sale_price')
                ) * models.F('sold_products__quantity')
            ),
            output_field=models.IntegerField()
        )

    }

    price_min_validator = MinValueValidator(0)

    title = models.CharField(
        verbose_name='Заголовок товара',
        max_length=120,
        null=False,
        blank=False,
        help_text='Укажите название товара (до 120 символов).',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    price = models.IntegerField(
        verbose_name='Цена товара',
        null=False,
        blank=False,
        validators=[
            price_min_validator
        ],
        help_text='Цена товара. Минимальное значение - 0 рублей.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
            'invalid': 'Некорректное значение для цены товара.'
        }
    )

    slug = AutoSlugField(
        null=False,
        blank=False,
        unique=True,
        editable=False,
        populate_from=lambda instance: f"товар-{instance.title}-{random_slug_number()}",
        unique_with=[
            'date_created'
        ],
        verbose_name='Ссылка на объект',
        help_text='Ссылка на объект генерируется автоматически. Используется для адресации в URL-адресах.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    quantity = models.IntegerField(
        verbose_name='Остаток на складе',
        validators=[
            MinValueValidator(0)
        ],
        null=False,
        blank=True,
        default=0,
        help_text='Укажите, сколько данного товара осталось на складе.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
        }
    )

    category = models.ForeignKey(
        'showroom.ProductCategory',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name=related_name,
        verbose_name='Категория',
        help_text='Укажите категорию товара.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
        }
    )

    showroom = models.ForeignKey(
        'showroom.Showroom',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name=related_name,
        verbose_name='Автосалон',
        help_text='Укажите автосалон, к которому должен быть привязан товар.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
        }
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        editable=False,
        verbose_name='Дата создания',
        help_text='Дата создания автосалона.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    def __str__(self):
        return self.title

    def sell(self, quantity, employee=None, sale_object=None):
        self.quantity -= quantity
        self.save()

        if not sale_object:
            sale_model = apps.get_model('showroom', 'ProductSale')
            sale_object = sale_model(
                showroom=self.showroom,
                employee=employee
            )
            sale_object.save()

        sale_item_model = apps.get_model('showroom', 'ProductSaleItem')

        sale_item_object = sale_item_model(
            product=self,
            sale=sale_object,
            quantity=quantity,
            sale_price=self.price
        )
        sale_item_object.save()
        return sale_object

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class ProductSaleItem(models.Model):
    """
    Модель, описывающая сущность проданного товара для истории продажи
    """

    related_name = 'sold_products'

    product = models.ForeignKey(
        'showroom.Product',
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        related_name=related_name,
        verbose_name='Проданный товар',
        help_text='Укажите, какой товар был продан.',
        error_messages={
            'required': 'Данное поля обязательно для заполнения.'
        }
    )

    sale = models.ForeignKey(
        'showroom.ProductSale',
        on_delete=models.CASCADE,
        verbose_name='Продажа',
        related_name=related_name,
        null=False,
        blank=False,
        help_text='Укажите, к какой продаже относится данный товар.',
        error_messages={
            'required': 'Данное поля обязательно для заполнения.',
            'invalid': 'Значение данного поля должно начинаться с 0'
        }
    )

    quantity = models.IntegerField(
        verbose_name='Кол-во проданного товара',
        validators=[
            MinValueValidator(0)
        ],
        null=False,
        blank=False,
        help_text='Укажите, какое кол-во данного товара было продано.',
        error_messages={
            'required': 'Данное поля обязательно для заполнения.',
            'invalid': 'Значение данного поля должно начинаться с 0'
        }

    )

    slug = AutoSlugField(
        null=False,
        blank=False,
        unique=True,
        editable=False,
        populate_from=lambda instance: f"товар-заказа-{instance.product.title}-{random_slug_number()}",
        unique_with=[
            'date_created'
        ],
        verbose_name='Ссылка на объект',
        help_text='Ссылка на объект генерируется автоматически. Используется для адресации в URL-адресах.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    sale_price = models.IntegerField(
        verbose_name='Цена проданного товара',
        null=False,
        blank=False,
        validators=[
            MinValueValidator(0)
        ],
        help_text='Укажите цену проданного товара за одну штуку.',
        error_messages={
            'required': 'Данное поля обязательно для заполнения.',
            'invalid': 'Значение данного поля должно начинаться с 0'
        }
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        editable=False,
        verbose_name='Дата создания',
        help_text='Дата создания товара продажи.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    def __str__(self):
        return str(self.product)

    class Meta:
        verbose_name = 'Товар продажи'
        verbose_name_plural = 'Товары продажи'


class ProductSale(models.Model):
    """
    Модель, описывающая сущность истории продажи товара пользователю
    """

    related_name = 'sales'

    employee = models.ForeignKey(
        'showroom.Employee',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name=related_name,
        verbose_name='Сотрудник',
        help_text='Укажите, какой сотрудник продал данные товары.',
        error_messages={
            'required': 'Данное поля обязательно для заполнения.'
        }

    )

    showroom = models.ForeignKey(
        'showroom.Showroom',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name=related_name,
        verbose_name='Автосалон',
        help_text='Укажите автосалон, к которому должен быть привязан товар.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
        }
    )

    slug = AutoSlugField(
        null=False,
        blank=False,
        unique=True,
        editable=False,
        populate_from=lambda instance: f"продажа-{instance.showroom.title}-{random_slug_number()}",
        verbose_name='Ссылка на объект',
        help_text='Ссылка на объект генерируется автоматически. Используется для адресации в URL-адресах.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        editable=False,
        verbose_name='Дата продажи',
        help_text='Дата продажи товаров.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    def __str__(self):
        return str(self.date_created)

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'


class ProductSupplyItem(models.Model):
    """
    Модель, описывающая сущность предмета поставки товара
    """

    related_name = 'supplied_products'

    product = models.ForeignKey(
        'showroom.Product',
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        related_name=related_name,
        verbose_name='Поставленный товар',
        help_text='Укажите, какой товар был поставлен.',
        error_messages={
            'required': 'Данное поля обязательно для заполнения.'
        }
    )

    supply = models.ForeignKey(
        'showroom.ProductSupply',
        on_delete=models.CASCADE,
        verbose_name='Поставка',
        related_name=related_name,
        null=False,
        blank=False,
        help_text='Укажите, к какой поставке относится данный товар.',
        error_messages={
            'required': 'Данное поля обязательно для заполнения.'
        }
    )

    quantity = models.IntegerField(
        verbose_name='Кол-во поставленного товара',
        validators=[
            MinValueValidator(0)
        ],
        null=False,
        blank=False,
        help_text='Укажите, какое кол-во данного товара было поставлено.',
        error_messages={
            'required': 'Данное поля обязательно для заполнения.'
        }

    )

    slug = AutoSlugField(
        null=False,
        blank=False,
        unique=True,
        editable=False,
        populate_from=lambda instance: f"товар-поставки-{instance.product.title}-{random_slug_number()}",
        unique_with=[
            'date_created'
        ],
        verbose_name='Ссылка на объект',
        help_text='Ссылка на объект генерируется автоматически. Используется для адресации в URL-адресах.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    supply_price = models.IntegerField(
        verbose_name='Цена поставленного товара',
        null=False,
        blank=False,
        validators=[
            MinValueValidator(0)
        ],
        help_text='Укажите цену поставленного товара за одну штуку.',
        error_messages={
            'required': 'Данное поля обязательно для заполнения.',
            'invalid': 'Значение данного поля должно начинаться с 0'
        }
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        editable=False,
        verbose_name='Дата поставки',
        help_text='Дата поставки товара.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    def __str__(self):
        return str(self.product)

    class Meta:
        verbose_name = 'Товар поставки'
        verbose_name_plural = 'Товары поставки'


class ProductSupply(models.Model):
    """
    Модель, описывающая сущность истории поставки товаров
    """
    related_name = 'supplies'

    dealer = models.ForeignKey(
        'showroom.Dealer',
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name=related_name,
        verbose_name='Дилер',
        help_text='Укажите дилера, к которому должна быть привязана поставка.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
        }
    )

    showroom = models.ForeignKey(
        'showroom.Showroom',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name=related_name,
        verbose_name='Автосалон',
        help_text='Укажите автосалон, к которому должна быть привязана поставка.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.',
        }
    )

    slug = AutoSlugField(
        null=False,
        blank=False,
        unique=True,
        editable=False,
        populate_from=lambda instance: f"поставка-{instance.showroom.title}-{random_slug_number()}",
        verbose_name='Ссылка на объект',
        help_text='Ссылка на объект генерируется автоматически. Используется для адресации в URL-адресах.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        editable=False,
        verbose_name='Дата продажи',
        help_text='Укажите дату совершения поставки.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    def __str__(self):
        return str(self.dealer)

    class Meta:
        verbose_name = 'Поставка товаров'
        verbose_name_plural = 'Поставки товаров'


class Dealer(AbstractStatisticsModel):
    """
    Модель, описывающая сущность дилера - поставщика товаров.
    """
    statistics_fields_verbose_names = {
        'supply_count': 'Кол-во поставок',
        'supply_product_count': 'Кол-во поставленных товаров всего',
        'supply_sales_count': 'Кол-во проданных товаров с поставок',

        'supply_sales_price_avg': 'Средняя цена продаваемого товара',
        'supply_sales_price_sum': 'Суммарная стоимость проданных товаров',
        'supply_sales_price_min': 'Минимальная стоимость проданных товаров',
        'supply_sales_price_max': 'Максимальная стоимость проданных товаров',

        'supply_sales_quantity_avg': 'Среднее кол-во заказываемого товара за раз',
        'supply_sales_quantity_sum': 'Суммарное кол-во заказанного товара',
        'supply_sales_quantity_min': 'Минимальное кол-во заказанного товара за раз',
        'supply_sales_quantity_max': 'Максимальное кол-во заказанного товара за раз',

        'supply_sales_profit_avg': 'Средняя выручка с продаваемого товара',
        'supply_sales_profit_sum': 'Суммарная выручка с продаваемого товара',
        'supply_sales_profit_min': 'Средняя выручка с продаваемого товара',
        'supply_sales_profit_max': 'Средняя выручка с продаваемого товара',
    }

    statistics_fields = {
        'supply_count': models.ExpressionWrapper(
            models.Count('supplies'),
            output_field=models.IntegerField()
        ),
        'supply_product_count': models.ExpressionWrapper(
            models.Count('supplies__supplied_products'),
            output_field=models.IntegerField()
        ),
        'supply_sales_count': models.ExpressionWrapper(
            models.Count('supplies__supplied_products__product__sales__sold_products'),
            output_field=models.IntegerField()
        ),

        # Статистика по цене продаваемого товара
        'supply_sales_price_avg': models.ExpressionWrapper(
            models.Avg('supplies__supplied_products__product__sales__sale_price'),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'supply_sales_price_sum': models.ExpressionWrapper(
            models.Sum('supplies__supplied_products__product__sales__sale_price'),
            output_field=models.IntegerField()
        ),
        'supply_sales_price_min': models.ExpressionWrapper(
            models.Min('supplies__supplied_products__product__sales__sale_price'),
            output_field=models.IntegerField()
        ),
        'supply_sales_price_max': models.ExpressionWrapper(
            models.Max('supplies__supplied_products__product__sales__sale_price'),
            output_field=models.IntegerField()
        ),

        # Статистика по кол-ву проданного товара
        'supply_sales_quantity_avg': models.ExpressionWrapper(
            models.Avg('supplies__supplied_products__product__sales__quantity'),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'supply_sales_quantity_sum': models.ExpressionWrapper(
            models.Sum('supplies__supplied_products__product__sales__quantity'),
            output_field=models.IntegerField()
        ),
        'supply_sales_quantity_min': models.ExpressionWrapper(
            models.Min('supplies__supplied_products__product__sales__quantity'),
            output_field=models.IntegerField()
        ),
        'supply_sales_quantity_max': models.ExpressionWrapper(
            models.Max('supplies__supplied_products__product__sales__quantity'),
            output_field=models.IntegerField()
        ),

        # Статистика по выручке
        'supply_sales_profit_avg': models.ExpressionWrapper(
            models.Avg(
                (
                    models.F('supplies__supplied_products__supply_price')
                    - models.F('supplies__supplied_products__product__sold_products__sale_price')
                ) * models.F('supplies__supplied_products__product__sold_products__quantity')
            ),
            output_field=models.DecimalField(decimal_places=2)
        ),
        'supply_sales_profit_sum': models.ExpressionWrapper(
            models.Sum(
                (
                        models.F('supplies__supplied_products__supply_price')
                        - models.F('supplies__supplied_products__product__sold_products__sale_price')
                ) * models.F('supplies__supplied_products__product__sold_products__quantity')
            ),
            output_field=models.IntegerField()
        ),
        'supply_sales_profit_max': models.ExpressionWrapper(
            models.Max(
                (
                        models.F('supplies__supplied_products__supply_price')
                        - models.F('supplies__supplied_products__product__sold_products__sale_price')
                ) * models.F('supplies__supplied_products__product__sold_products__quantity')
            ),
            output_field=models.IntegerField()
        ),
        'supply_sales_profit_min': models.ExpressionWrapper(
            models.Min(
                (
                        models.F('supplies__supplied_products__supply_price')
                        - models.F('supplies__supplied_products__product__sold_products__sale_price')
                ) * models.F('supplies__supplied_products__product__sold_products__quantity')
            ),
            output_field=models.IntegerField()
        )

    }

    name = models.CharField(
        verbose_name='Имя дилера',
        max_length=50,
        null=False,
        blank=False,
        unique=True,
        help_text='Укажите название дилера.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    slug = AutoSlugField(
        null=False,
        blank=False,
        unique=True,
        editable=False,
        populate_from=lambda instance: f"дилер-{instance.name}-{random_slug_number()}",
        unique_with=[
            'date_created'
        ],
        verbose_name='Ссылка на объект',
        help_text='Ссылка на объект генерируется автоматически. Используется для адресации в URL-адресах.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        editable=False,
        verbose_name='Дата добавления',
        help_text='Дата добавления дилера.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    is_active = models.BooleanField(
        verbose_name='Дилер активен',
        default=True,
        blank=False,
        null=False,
        help_text='Отметьте, если хотите сделать дилера активный или наоборот.',
        error_messages={
            'required': 'Данное поле обязательно для заполнения.'
        }
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Дилер'
        verbose_name_plural = 'Дилеры'
