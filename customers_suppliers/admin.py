from django.contrib import admin
from customers_suppliers.models import CustomUser, Customer, Supplier


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'user_type']
    list_filter = ['id', 'email', 'user_type']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'phone_number']
    list_filter = ['id']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['id','name_organization', 'user', 'contact_person', 'supplier_type', 'inn']
    list_filter = ['id', 'name_organization']