from django import forms
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from . import models


class ShowroomForm(forms.ModelForm):
    """
    Универсальная форма для модели автосалона
    """
    model = models.Showroom

    class Meta:
        widgets = {
            'phone_number': PhoneNumberPrefixWidget()
        }
        exclude = ['owner', 'slug']


class ShowroomAdminForm(forms.ModelForm):
    """
    Форма для редактирования и добавления данных по модели автосалона
    Только для админ-панели
    """

    model = models.Showroom

    class Meta:
        widgets = {
            'phone_number': PhoneNumberPrefixWidget()
        }


class EmployeeAdminForm(forms.ModelForm):
    """
    Форма для редактирования и добавления данных по модели автосалона
    Только для админ-панели
    """

    model = models.Employee

    class Meta:
        widgets = {
            'phone_number': PhoneNumberPrefixWidget()
        }


class EmployeeForm(forms.ModelForm):
    """
    Универсальная форма для модели сотрудника
    """

    model = models.Employee

    class Meta:
        widgets = {
            'phone_number': PhoneNumberPrefixWidget()
        }
        exclude = ['showroom', 'slug']


class ProductCategoryForm(forms.ModelForm):
    """
    Универсальная форма для модели категории товара
    """

    model = models.ProductCategory

    class Meta:
        exclude = ['showroom', 'slug']


class ProductForm(forms.ModelForm):
    """
    Универсальная форма для модели товара
    """

    model = models.Product

    class Meta:
        exclude = ['showroom', 'slug']


class ProductSaleItemForm(forms.ModelForm):
    """
    Универсальная форма для модели товара продажи
    """

    model = models.ProductSaleItem

    class Meta:
        exclude = ['slug']


class ProductSaleForm(forms.ModelForm):
    """
    Универсальная форма для модели продажи
    """

    model = models.ProductSale

    class Meta:
        exclude = ['showroom', 'slug']


class ProductSupplyItemForm(forms.ModelForm):
    """
    Универсальная форма для модели товара поставки
    """

    model = models.ProductSupplyItem

    class Meta:
        exclude = ['slug']


class ProductSupplyForm(forms.ModelForm):
    """
    Универсальная форма для модели поставки
    """

    model = models.ProductSupply

    class Meta:
        exclude = ['showroom', 'slug']


class DealerForm(forms.ModelForm):
    """
    Универсальная форма для модели дилера
    """

    model = models.Dealer

    class Meta:
        exclude = ['showroom', 'slug']
