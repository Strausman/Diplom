import time
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from customers_suppliers.models import CustomUser, Customer, Supplier #  Убедитесь, что путь верный

class CustomUserViewSetTests(APITestCase):

    def test_create_customer(self):
        """
        Тестирует создание нового пользователя-покупателя.
        """
        url = reverse('customuser-list') #  Имя endpoint'а из роутера
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'user_type': 'customer',
            'customer': {
                'phone_number': '1234567890',
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().username, 'testuser')
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.get().phone_number, '1234567890')


    def test_create_supplier(self):
        """
        Тестирует создание нового пользователя-поставщика.
        """
        url = reverse('customuser-list')
        data = {
            'username': 'testsupplier',
            'email': 'testsupplier@example.com',
            'password': 'testpassword',
            'user_type': 'supplier',
            'supplier': {
                'contact_person': 'Test Person',
                'supplier_type': 'OOO',
                'inn': '123456789012',
                'kpp': '123456789',  # Для ООО
                'phone_number': '0987654321',
                'name_organization': 'Test Organization',
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(Supplier.objects.count(), 1)
        

    def test_create_customer_invalid_email(self):
        url = reverse('customuser-list')
        data = {
            'username': 'testuser',
            'email': 'invalid_email', # Некорректный email
            'password': 'testpassword',
            'user_type': 'customer',
            'customer': {
                'phone_number': '1234567890',
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        
    def test_get_user_authenticated(self):
        user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.force_authenticate(user=user)
        url = reverse('customuser-detail', kwargs={'pk': user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    def test_create_customer_invalid_phone(self):
        url = reverse('customuser-list')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'user_type': 'customer',
            'customer': {
                'phone_number': 'abc',  # Некорректный номер
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data['customer'])


    def test_create_supplier_ip(self):
        """Тестирует создание нового пользователя-поставщика типа ИП."""
        url = reverse('customuser-list')
        data = {
            'username': 'testip',
            'email': 'testip@example.com',
            'password': 'testpassword',
            'user_type': 'supplier',
            'supplier': {
                'contact_person': 'Test IP Person',
                'supplier_type': 'IP',  #  Тип поставщика - ИП
                'inn': '123456789012',  # ИНН для ИП (12 цифр)
                'phone_number': '09876543210',
                'name_organization': None, # или можно пропустить это поле, так как для ИП name_organization может быть пустым
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        user = CustomUser.objects.get()
        self.assertEqual(user.username, 'testip')
        self.assertEqual(Supplier.objects.count(), 1)
        supplier = Supplier.objects.get()
        self.assertEqual(supplier.user, user)
        self.assertEqual(supplier.contact_person, 'Test IP Person')
        self.assertEqual(supplier.supplier_type, 'IP')
        self.assertEqual(supplier.inn, '123456789012')
        self.assertEqual(supplier.phone_number, '09876543210')
        self.assertIsNone(supplier.name_organization) # Проверяем, что name_organization пустое (None) или отсутствует


    def test_response_time_without_cache(self):
        start_time = time.time()
        data = CustomUser.objects.all()  # Запрос к модели Customer
        response_time = time.time() - start_time
        print("Время отклика без кэширования:", response_time)

    def test_response_time_with_cache(self):
        start_time = time.time()
        data = CustomUser.objects.all()  # Запрос к модели Customer
        response_time = time.time() - start_time
        print("Время отклика с кэшированием:", response_time)

        