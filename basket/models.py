from django.db import models
from customers_suppliers.models import Customer, Supplier
from products.models import ProductInfo
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', filename='load_data.log')
logger = logging.getLogger('basket')



class Cart(models.Model):
    CART_TYPE_CHOICES = {
        ('collecting order', 'сбор заказа'),
        ('waiting for confirmation', 'ожидание подтверждения'),
        ('cancelled', 'отменён'),
        ('confirmed', 'подтверждён'),
    }
    cart_type = models.CharField(max_length=50 , choices=CART_TYPE_CHOICES, default='collecting order', verbose_name='Статус')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='carts', verbose_name='Покупатель')
    products = models.ManyToManyField(ProductInfo, related_name='carts', verbose_name='Товар', through='CartProduct')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    adress = models.CharField(max_length=255, verbose_name='Адрес', blank=False, null=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
    
    def __str__(self):
        return f'Корзина пользователя: id-{self.id} - {self.customer}. сумма {self.update_total_amount()}, статус: {self.cart_type}.'
    
    def update_total_amount(self):
        total_amount = sum(item.product.price * item.quantity for item in self.cart_products.all())
        return total_amount
    
    def add_product(self, product, quantity):
        cart_product, created = self.cart_products.get_or_create(product=product)
        cart_product.quantity += quantity
        cart_product.save()
        return self.update_total_amount()

    def remove_product(self, product):
        self.cart_products.filter(product=product).delete()
        return self.update_total_amount()

    def update_product_quantity(self, product, quantity):
        cart_product = self.cart_products.get(product=product)
        cart_product.quantity = quantity
        cart_product.save()
        return self.update_total_amount()
    
    def confirm_order(self):
        if self.cart_type == 'collecting order':
            self.cart_type = 'waiting for confirmation'
            self.save()
            return True
        return False

    def cancel_order(self):
        if self.cart_type in ['collecting order', 'waiting for confirmation']:
            self.cart_type = 'cancelled'
            self.save()
            return True
        return False

    def confirm_payment(self):
        if self.cart_type == 'waiting for confirmation':
            self.cart_type = 'confirmed'
            self.save()
            return True
        return False


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_products', verbose_name='Корзина')
    product = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='cart_products', verbose_name='Товар')
    quantity = models.IntegerField(default=1, verbose_name='Количество')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='Поставщик')

    class Meta:
        unique_together = ('cart', 'product')  
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'

    def save(self, *args, **kwargs):
        """Переопределение метода save для проверки количества."""
        if self.quantity <= 0:
            raise ValueError("Количество должно быть положительным.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product} (Количество: {self.quantity}) в корзине {self.cart}'
