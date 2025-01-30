from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from customers_suppliers.models import Customer, CustomUser
from basket.models import Cart, CartProduct
from products.models import Product, Category, ProductInfo, Supplier

class CartTests(APITestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(username='testcustomer', email='testcustomer@example.com', password='testpassword', user_type='customer')
        self.customer_instance = Customer.objects.create(user=self.customer, phone_number='1234567890')
        self.supplier = CustomUser.objects.create_user(username='testsupplier', email='testsupplier@example.com', password='testpassword', user_type='supplier')
        self.supplier_instance = Supplier.objects.create(user=self.supplier, supplier_type='IP', inn='123456789012')

        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(name='Test Product', category=self.category)
        self.product_info = ProductInfo.objects.create(model='Test Model', external_id=123, product=self.product, shop=self.supplier_instance, quantity=10, price=100, price_rrc=120)

        self.client = APIClient()

    def test_create_cart(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('basket:create-cart')
        data = {'customer': self.customer_instance.id, 'cart_type': 'collecting order', 'adress': 'Test adress'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cart.objects.count(), 1)
        cart = Cart.objects.get()
        self.assertEqual(cart.customer, self.customer_instance)
        self.assertEqual(cart.cart_type, 'collecting order')
        self.assertEqual(cart.adress, 'Test adress')

    def test_get_cart(self):
        self.client.force_authenticate(user=self.customer)

        cart = Cart.objects.create(customer=self.customer_instance, cart_type='collecting order', adress='Test adress')


        url = reverse('basket:get-cart', kwargs={'pk': cart.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], cart.id) # Проверка id
        self.assertEqual(response.data['customer'], self.customer_instance.id)  # Проверка customer
        self.assertEqual(response.data['cart_type'], 'collecting order') # Проверка типа корзины
        self.assertEqual(response.data['adress'], 'Test adress')

    def test_get_carts_unauthorized(self):
        url = reverse('basket:get-carts')
        response = self.client.get(url)  # Запрос без авторизации
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)