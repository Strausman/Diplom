from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from order.models import Category, Parameter, Product, ProductInfo, ProductParameter
from order.serializers import CategorySerializer, ParameterSerializer, ProductInfoSerializer, ProductParameterSerializer, ProductSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser


class PerrmissionMixin:
    
    def check_admin_permission(self, allowed_actions=None):
        if allowed_actions is None:
            allowed_actions = []
        if self.request.user.is_staff:
            return [AllowAny()]
        if self.action in allowed_actions:
            return [AllowAny()]
        if self.request.user.is_authenticated:
            if self.request.user.user_type == 'customer':
                if self.action in allowed_actions:
                    return [AllowAny()]
                else:
                    raise PermissionDenied("У вас нет разрешения на это действие.")
        return [IsAuthenticated()]
    

class CategoryViewSet(PerrmissionMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['id', 'name']
    
    def get_permissions(self):
        return self.check_admin_permission(allowed_actions=['list', 'retrieve'])
            
        
class ProductViewSet(PerrmissionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['id', 'name', 'category']
    
    def get_permissions(self):
        return self.check_admin_permission(allowed_actions=['list', 'retrieve'])
    

class ProductInfoViewSet(PerrmissionMixin, viewsets.ModelViewSet):
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
    filterset_fields = ['id', 'model', 'external_id', 'product', 'shop', 'quantity', 'price', 'price_rrc']

    def get_permissions(self):
        return self.check_admin_permission(allowed_actions=['list', 'retrieve'])


class ParameterViewSet(PerrmissionMixin, viewsets.ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    filterset_fields = ['id', 'name']
    
    def get_permissions(self):
        return self.check_admin_permission(allowed_actions=['list', 'retrieve'])
    

class ProductParameterViewSet(PerrmissionMixin, viewsets.ModelViewSet):
    queryset = ProductParameter.objects.all()
    serializer_class = ProductParameterSerializer
    filterset_fields = ['id', 'product_info', 'parameter', 'value']
    
    def get_permissions(self):
        return self.check_admin_permission(allowed_actions=['list', 'retrieve'])