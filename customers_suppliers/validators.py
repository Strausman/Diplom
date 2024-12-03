from django.core.exceptions import ValidationError
from rest_framework import serializers


class CustomValidators:
    @staticmethod
    def vadate_inn(value):
        """Проверка ИНН на корректность"""
        if not value.isdigit() or len(value) not in [10, 12]:
            raise ValidationError('Инн должен состоять из 10 или 12 цифр')
    
    @staticmethod
    def validate_phone(value):
        """Проверка номера телефона на корректность"""
        if not value.isdigit() or len(value) < 10:
            raise ValidationError('Номер телефона должен содержать не менее 10 цифр')
        
    @staticmethod
    def validate_kpp_for_ooo(supplier):
        """Проверка КПП для ООО"""
        if supplier.supplier_type == 'OOO' and not supplier.kpp:
            raise ValidationError('Поле КПП обязательно для поставщиков типа "ООО".')
        elif supplier.supplier_type == 'IP' and supplier.kpp:
            raise ValidationError('Поле КПП не обязательное для поставщиков типа "ИП".')
        
    @staticmethod
    def validate_kpp_for_ooo_serializer(attrs):
        """Проверка КПП для ООО"""
        supplier_type = attrs.get('supplier_type')
        kpp = attrs.get('kpp')
    
        if supplier_type == 'OOO' and not kpp:
            raise ValidationError('Поле КПП обязательно для поставщиков типа "ООО".')
        elif supplier_type == 'IP' and kpp:
            raise ValidationError('Поле КПП не обязательное для поставщиков типа "ИП".')
        
    @staticmethod
    def validate_user_type(attrs):
        """Проверка типа пользователя"""
        user_type = attrs.get('user_type')
        
        if user_type not in ['customer', 'supplier']:
            raise serializers.ValidationError("user_type должен быть 'customer' или 'supplier'")
        if user_type == 'customer':
            if 'customer' not in attrs:
                raise serializers.ValidationError("Необходимо предоставить данные для создания клиента.")
            if 'supplier' in attrs:
                raise serializers.ValidationError("Данные поставщика не могут быть предоставлены для клиента.")
        if user_type == 'supplier':
            if 'supplier' not in attrs:
                raise serializers.ValidationError("Необходимо предоставить данные для создания поставщика.")
            if 'customer' in attrs:
                raise serializers.ValidationError("Данные клиента не могут быть предоставлены для поставщика.")
        
        return attrs