from rest_framework import serializers
from django.forms import ValidationError

from .models import CustomUser, Customer, Supplier
from customers_suppliers.validators import CustomValidators


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'phone_number']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'contact_person',
                  'supplier_type', 'inn',
                  'kpp', 'phone_number',
                  'name_organization']
        
    def validate(self, attrs):
        CustomValidators.validate_kpp_for_ooo_serializer(attrs)
        return attrs

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    customer = CustomerSerializer(required=False)
    supplier = SupplierSerializer(required=False)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'user_type',
                  'email', 'customer', 'supplier', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, attrs):
        CustomValidators.validate_user_type(attrs)
        return attrs
        
    def create(self, validated_data):
        customer_data = validated_data.pop('customer', None)
        supplier_data = validated_data.pop('supplier', None)
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            user_type=validated_data['user_type']
        )
        user.set_password(validated_data['password'])
        user.save()
        if validated_data['user_type'] == 'customer':
            Customer.objects.create(user=user, **customer_data)
        elif validated_data['user_type'] == 'supplier':
            Supplier.objects.create(user=user, **supplier_data)
        return user


