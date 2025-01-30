from django.test import TestCase

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from customers_suppliers.models import CustomUser, Supplier
from products.models import Category, Parameter, Product, ProductInfo, ProductParameter




class ProductViewSetTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(name="Test Product", category=self.category)

        self.customer = CustomUser.objects.create_user(username='testcustomer', email='testcustomer@example.com', password='testpassword', user_type='customer')
        self.supplier = CustomUser.objects.create_user(username='testsupplier', email='testsupplier@example.com', password='testpassword', user_type='supplier')
        self.supplier_instance = Supplier.objects.create(user=self.supplier, supplier_type='IP', inn='123456789012') #  Создаем экземпляр Supplier и присваиваем его self.supplier_instance
        self.admin = CustomUser.objects.create_superuser(username='testadmin', email='testadmin@example.com', password='testpassword')


        self.product_info = ProductInfo.objects.create(
            model="Test Model", external_id=1, product=self.product, shop=self.supplier_instance, #  Используем self.supplier_instance
            quantity=10, price=100, price_rrc=120
        )
        self.parameter = Parameter.objects.create(name="Test Parameter")
        self.product_parameter = ProductParameter.objects.create(product_info=self.product_info, parameter=self.parameter, value="Test Value")

        self.client = APIClient()


    def test_list_product_unauthorized(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_list_product_customer(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_list_product_supplier(self):
        self.client.force_authenticate(user=self.supplier)
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_product_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_retrieve_product_unauthorized(self):
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Product")

    def test_retrieve_product_customer(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Product")

    def test_retrieve_product_supplier(self):
        self.client.force_authenticate(user=self.supplier)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Product")

    def test_retrieve_product_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Product")
        
    def test_create_product_unauthorized(self):
        url = reverse('product-list')
        data = {'name': 'New Product', 'category': self.category.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) #  403 для неавторизованного пользователя

    def test_create_product_customer(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('product-list')
        data = {'name': 'New Product', 'category': self.category.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) #  403 для customer

    def test_create_product_supplier(self):
        self.client.force_authenticate(user=self.supplier)
        url = reverse('product-list')
        data = {'name': 'New Product', 'category': self.category.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) #  Теперь ожидаем 201
        self.assertEqual(Product.objects.count(), 2)  # Проверяем, что продукт создан

    def test_create_product_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('product-list')
        data = {'name': 'New Product', 'category': self.category.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) # 201 для admin
        self.assertEqual(Product.objects.count(), 2)  # Проверяем, что продукт создан

    def test_update_product_unauthorized(self):
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        data = {'name': 'Updated Product'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_customer(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        data = {'name': 'Updated Product'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_supplier(self):
        self.client.force_authenticate(user=self.supplier)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        data = {'name': 'Updated Product'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK) # Supplier может обновлять
        self.assertEqual(Product.objects.get(pk=self.product.id).name, "Updated Product") #  Проверяем изменение имени

    def test_update_product_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        data = {'name': 'Updated Product'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK) # Admin может обновлять
        self.assertEqual(Product.objects.get(pk=self.product.id).name, "Updated Product") #  Проверяем изменение имени

    def test_partial_update_product_unauthorized(self):
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        data = {'name': 'Partially Updated Product'}
        response = self.client.patch(url, data)  # Используем patch
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_product_customer(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        data = {'name': 'Partially Updated Product'}
        response = self.client.patch(url, data)  # Используем patch
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_product_supplier(self):
        self.client.force_authenticate(user=self.supplier)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        data = {'name': 'Partially Updated Product'}
        response = self.client.patch(url, data)  # Используем patch
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk=self.product.id).name, "Partially Updated Product")

    def test_partial_update_product_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        data = {'name': 'Partially Updated Product'}
        response = self.client.patch(url, data)  # Используем patch
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk=self.product.id).name, "Partially Updated Product")
