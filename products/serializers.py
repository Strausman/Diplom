from rest_framework import serializers
from customers_suppliers.validators import CustomValidators
from .models import Category, Product, ProductInfo, Parameter, ProductParameter
import logging


logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='log.txt')



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name',]
        

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category']
        

class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ['id', 'model', 'external_id', 'product', 'shop', 'quantity', 'price', 'price_rrc']
        

class ProductInfoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ['id', 'model', 'external_id', 'product', 'quantity', 'price', 'price_rrc']
    
         
class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['id', 'name']        


class ProductParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductParameter
        fields = ['id', 'product_info', 'parameter', 'value']