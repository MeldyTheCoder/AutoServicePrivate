from django import forms
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from AutoServiceAdmin.forms import CrispyForm
import django_tables2 as tables
from . import models


class ShowroomForm(CrispyForm, forms.ModelForm):
    """
    Универсальная форма для модели автосалона
    """

    submit_field = 'Изменить'

    model = models.Showroom

    class Meta:
        model = models.Showroom
        widgets = {
            'phone_number': PhoneNumberPrefixWidget()
        }
        exclude = ['owner', 'slug']


class ShowroomDeletionForm(CrispyForm, forms.Form):
    """
    Форма для удаления автосалона
    """

    submit_field = 'Удалить'


class ShowroomAdminForm(CrispyForm, forms.ModelForm):
    """
    Форма для редактирования и добавления данных по модели автосалона
    Только для админ-панели
    """

    submit_field = 'Изменить'

    model = models.Showroom

    class Meta:
        widgets = {
            'phone_number': PhoneNumberPrefixWidget()
        }


class EmployeeAdminForm(CrispyForm, forms.ModelForm):
    """
    Форма для редактирования и добавления данных по модели автосалона
    Только для админ-панели
    """

    submit_field = 'Изменить'

    model = models.Employee

    class Meta:
        widgets = {
            'phone_number': PhoneNumberPrefixWidget()
        }


class EmployeeForm(CrispyForm, forms.ModelForm):
    """
    Универсальная форма для модели сотрудника
    """

    submit_field = 'Изменить'

    model = models.Employee

    class Meta:
        widgets = {
            'phone_number': PhoneNumberPrefixWidget()
        }
        exclude = ['showroom', 'slug']


class EmployeeTable(tables.Table):
    """
    Табличное отображение модели сотрудника
    """

    class Meta:
        attrs = {"class": "table table-striped table-bordered"}
        model = models.Employee
        exclude = ['showroom', 'slug']


class ProductCategoryForm(CrispyForm, forms.ModelForm):
    """
    Универсальная форма для модели категории товара
    """

    submit_field = 'Изменить'

    model = models.ProductCategory

    class Meta:
        exclude = ['showroom', 'slug']


class ProductCategoryTable(tables.Table):
    """
    Табличное отображение модели категории товара
    """

    class Meta:
        attrs = {"class": "table table-striped table-bordered"}
        model = models.ProductCategory
        exclude = ['showroom', 'slug']


class ProductForm(CrispyForm, forms.ModelForm):
    """
    Универсальная форма для модели товара
    """

    submit_field = 'Изменить'

    model = models.Product

    class Meta:
        exclude = ['showroom', 'slug']


class ProductTable(tables.Table):
    """
    Табличное отображение модели товара
    """

    class Meta:
        attrs = {"class": "table table-striped table-bordered"}
        model = models.Product
        exclude = ['showroom', 'slug']


class ProductSaleItemForm(CrispyForm, forms.ModelForm):
    """
    Универсальная форма для модели товара продажи
    """

    submit_field = 'Изменить'

    model = models.ProductSaleItem

    class Meta:
        exclude = ['slug']


class ProductSaleItemTable(tables.Table):
    """
    Табличное отображение модели товара продажи
    """

    class Meta:
        attrs = {"class": "table table-striped table-bordered"}
        model = models.ProductSaleItem
        exclude = ['slug']


class ProductSaleForm(CrispyForm, forms.ModelForm):
    """
    Универсальная форма для модели продажи
    """

    submit_field = 'Изменить'

    model = models.ProductSale

    class Meta:
        exclude = ['showroom', 'slug']


class ProductSaleTable(tables.Table):
    """
    Табличное отображение модели продажи
    """

    class Meta:
        attrs = {"class": "table table-striped table-bordered"}
        model = models.ProductSale
        exclude = ['showroom', 'slug']


class ProductSupplyItemForm(CrispyForm, forms.ModelForm):
    """
    Универсальная форма для модели товара поставки
    """

    submit_field = 'Изменить'

    model = models.ProductSupplyItem

    class Meta:
        exclude = ['slug']


class ProductSupplyItemTable(tables.Table):
    """
    Табличное отображение модели предмета поставки
    """

    class Meta:
        attrs = {"class": "table table-striped table-bordered"}
        model = models.ProductSupplyItem
        exclude = ['slug']


class ProductSupplyForm(CrispyForm, forms.ModelForm):
    """
    Универсальная форма для модели поставки
    """

    submit_field = 'Изменить'

    model = models.ProductSupply

    class Meta:
        exclude = ['showroom', 'slug']


class ProductSupplyTable(tables.Table):
    """
    Табличное отображение модели поставки
    """

    class Meta:
        attrs = {"class": "table table-striped table-bordered"}
        model = models.ProductSupply
        exclude = ['showroom', 'slug']


class DealerForm(CrispyForm, forms.ModelForm):
    """
    Универсальная форма для модели дилера
    """

    submit_field = 'Изменить'

    model = models.Dealer

    class Meta:
        exclude = ['showroom', 'slug']


class DealerTable(tables.Table):
    """
    Табличное отображение модели дилера
    """

    class Meta:
        attrs = {"class": "table table-striped table-bordered"}
        model = models.Dealer
        exclude = ['showroom', 'slug']
