from django.contrib import admin
from . import models, forms
from django.db.models import Sum, Count, F
# Register your models here.


@admin.register(models.Showroom)
class ShowroomAdmin(admin.ModelAdmin):
    form = forms.ShowroomAdminForm
    list_filter = ['date_created']
    list_display = ['id', 'title', 'owner_fullname', 'phone_number', 'date_created']
    readonly_fields = ['slug', 'date_created']
    list_display_links = ['id', 'title']

    @admin.display(description='Владелец', empty_value='--')
    def owner_fullname(self, object):
        if object and object.owner:
            return object.owner.get_full_name()


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'product_price', 'category', 'showroom']
    readonly_fields = ['slug', 'date_created']
    list_filter = ['date_created']
    list_display_links = ['id', 'title']

    @admin.display(description='Цена', empty_value='--')
    def product_price(self, object):
        if object and object.price:
            return f'{object.price} RUB'


@admin.register(models.ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'showroom', 'date_created']
    list_filter = ['date_created']
    readonly_fields = ['date_created', 'slug']
    list_display_links = ['id', 'name']


@admin.register(models.ProductSupply)
class ProductSupplyAdmin(admin.ModelAdmin):
    list_display = ['id', 'dealer', 'showroom', 'supply_price_total', 'date_created']
    list_filter = ['date_created']
    list_display_links = ['id']
    readonly_fields = ['date_created', 'slug']

    @admin.display(description='Цена поставки', empty_value='0 RUB')
    def supply_price_total(self, object):
        if object:
            total_price = object.supplied_products.aggregate(sum=Sum(F('supply_price') * F('quantity')))['sum']
            return f'{total_price} RUB'


@admin.register(models.ProductSupplyItem)
class ProductsSupplyItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'supply', 'quantity', 'supply_price_total']
    list_filter = ['date_created']
    readonly_fields = ['date_created', 'slug']

    @admin.display(description='Цена поставки', empty_value='0 RUB')
    def supply_price_total(self, object):
        if object and object.supply_price and object.quantity:
            total_price = object.supply_price * object.quantity
            return f'{total_price} RUB'


@admin.register(models.ProductSale)
class ProductSaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'showroom', 'sale_price_total', 'date_created']
    list_filter = ['date_created']
    readonly_fields = ['date_created', 'slug']

    @admin.display(description='Стоимость продажи', empty_value='0 RUB')
    def sale_price_total(self, object):
        if object:
            total_price = object.sold_products.aggregate(sum=Sum(F('sale_price') * F('quantity')))['sum']
            return f'{total_price} RUB'


@admin.register(models.ProductSaleItem)
class ProductSaleItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'sale', 'quantity', 'sale_price_total', 'date_created']
    list_filter = ['date_created']
    readonly_fields = ['date_created', 'slug']

    @admin.display(description='Стоимость продажи', empty_value='0 RUB')
    def sale_price_total(self, object):
        if object and object.sale_price and object.quantity:
            total_price = object.sale_price * object.quantity
            return f'{total_price} RUB'


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = forms.EmployeeAdminForm
    list_display = ['id', 'full_name', 'phone_number', 'showroom', 'date_created']
    list_filter = ['date_created', 'is_restricted']
    readonly_fields = ['date_created', 'slug']

    @admin.display(description='Полное имя', empty_value='--')
    def full_name(self, object):
        if object:
            return f"{object.first_name} {object.last_name} {object.surname}"


@admin.register(models.Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'date_created']
    list_filter = ['date_created', 'is_active']
    list_display_links = ['id', 'name']
    readonly_fields = ['date_created', 'slug']
