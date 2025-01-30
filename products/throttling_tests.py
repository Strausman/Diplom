from rest_framework.test import APITestCase
from django.urls import reverse
from customers_suppliers.models import CustomUser
from products.models import Category, Product
from rest_framework import status

class ThrottlingTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(name="Test Product", category=self.category)

        self.customer = CustomUser.objects.create_user(username='testcustomer', email='testcustomer@example.com', password='testpassword', user_type='customer')

    def test_throttling_unauthorized(self):
        url = reverse('product-list')
        for _ in range(101):  # Пробуем сделать 101 запрос
            response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)  # Ожидаем 429

    def test_throttling_authenticated_user(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('product-list')
        for _ in range(1001):  # Пробуем сделать 1001 запрос
            response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)  # Ожидаем 429
