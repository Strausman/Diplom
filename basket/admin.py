from django.contrib import admin

from basket.models import Cart, CartProduct

# Register your models here.
class OrderPositionInline(admin.TabularInline):
    model = CartProduct
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [OrderPositionInline, ]
    pass


@admin.register(CartProduct)
class CartProductAdmin(admin.ModelAdmin):
    pass