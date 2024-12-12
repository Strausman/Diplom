from django.contrib.auth.models import AbstractUser, User 
from django.db import models
from .validators import CustomValidators

# Create your models here.

USER_TYPE_CHOICES = [
    ('customer', 'Покупатель'),
    ('supplier', 'Поставщик'),
]

SUPPLIER_TYPE_CHOICES = [
    ('OOO', 'Общество с ограниченной ответственностью'),
    ('IP', 'Индивидуальный предприниматель'),
]


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.email})"



class Customer(models.Model):
    user = models.OneToOneField(CustomUser, related_name='customer', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True, validators=[CustomValidators.validate_phone])

    def __str__(self):
        return f"{self.user.username} (Клиент)"
    

class Supplier(models.Model):
    user = models.OneToOneField(CustomUser , related_name='supplier', on_delete=models.CASCADE)
    contact_person = models.CharField(max_length=50, blank=True, null=True)
    supplier_type = models.CharField(max_length=10, choices=SUPPLIER_TYPE_CHOICES, default=None)
    inn = models.CharField(max_length=12, blank=False, null=False, validators=[CustomValidators.vadate_inn])    
    kpp = models.CharField(max_length=12, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    name_organization = models.CharField(max_length=250, blank=True, null=True)
    
    def clean(self):
        super().clean()
        CustomValidators.validate_kpp_for_ooo(self)
        
    def __str__(self):
        if not self.name_organization:
            return f"ИП {self.user.username} (Поставщик)"
        return f"{self.name_organization} (Поставщик)"
