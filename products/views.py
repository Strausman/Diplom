import logging
from django.db import IntegrityError
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied, NotFound
import yaml
from customers_suppliers import serializers
from customers_suppliers.models import Supplier
from products.models import Category, Parameter, Product, ProductInfo, ProductParameter
from products.serializers import (
    CategorySerializer, 
    ParameterSerializer, 
    ProductInfoCreateSerializer, 
    ProductInfoSerializer, 
    ProductParameterSerializer, 
    ProductSerializer
)
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', filename='load_data.log')
logger = logging.getLogger(__name__)
logger.info("Логирование инициализировано.")

class PermissionMixin:
    def allowed_actions_permission(self, allowed_actions=None):
        return allowed_actions or ['list', 'retrieve']
    
    def check_user_type(self, user_type):
        return self.request.user.is_authenticated and self.request.user.user_type == user_type
    
    def check_admin(self):
        return self.request.user.is_staff
    
    def check_creator(self, product_id):
        logger.info('Инициализация функции проверки создателя')
        if not self.request.user.is_authenticated:
            logger.info('False')
            return False
        try:
            product_info_instance = ProductInfo.objects.get(id=product_id)
            logger.info('Продукт найден: %s', product_info_instance)
        except ObjectDoesNotExist:
            logger.error("Продукт с указанным ID не найден: %s", product_id)
            raise NotFound(detail="Продукт с указанным ID не найден.")
        supplier_user = product_info_instance.shop.user
        is_creator = supplier_user.id == self.request.user.id
        logger.info(f'Проверка создателя: %s', is_creator)
        
        return is_creator
    
    def get_permissions_mixin(self):
        if self.check_admin():
            logger.info('Доступ предоставлен: пользователь является администратором.')
            return [AllowAny()]
        
        if self.check_user_type('supplier'):
            logger.info('Доступ предоставлен: пользователь является поставщиком.')
            return [AllowAny()]
        
        if self.check_user_type('customer') and self.action in self.allowed_actions_permission():
            logger.info('Доступ предоставлен: покупатель использует разрешенные методы.')
            return [AllowAny()]
        
        if self.action in self.allowed_actions_permission():
            logger.info('Доступ предоставлен: аноним использует разрешенные методы.')
            return [AllowAny()]
        
        logger.warning('Доступ отклонен: у пользователя нет прав.')
        raise PermissionDenied("Нет прав.")
    
        
class CategoryViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['id', 'name']
    
    def get_permissions(self):
        return self.get_permissions_mixin()

class ProductViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['id', 'name', 'category']
    
    def get_permissions(self):
        logger.info(f'Пользователь {self.request.user} пытается получить доступ к действию: {self.action}')
        return self.get_permissions_mixin()

class ProductInfoViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = ProductInfo.objects.all()
    filterset_fields = ['id', 'model', 'external_id', 'product', 'shop', 'quantity', 'price', 'price_rrc']
    
    def get_serializer_class(self):
        if self.request.user.is_staff:
            return ProductInfoSerializer 
        return ProductInfoCreateSerializer if self.action in ['create', 'update', 'partial_update', 'destroy'] else ProductInfoSerializer 

    def get_permissions(self):
        if self.check_admin():
            return [AllowAny()]
        if self.action in self.allowed_actions_permission():
            return [AllowAny()]
        if self.check_user_type('supplier'):
            if self.action in self.allowed_actions_permission() or self.action == 'create':
                return [AllowAny()]
            product_id = self.kwargs.get('pk')
            if self.check_creator(product_id):
                return [AllowAny()]
        raise PermissionDenied("Нет прав.")
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            if self.request.user.is_staff:
                self.perform_create(serializer)
            else:
                supplier = request.user.supplier
                serializer.save(shop=supplier)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            logger.error("IntegrityError: Дублирующая запись для Product Info.")
            raise serializers.ValidationError("Эта информация о продукте уже существует для данного продукта и магазина.")
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object() 
            logger.info(instance)
        except Http404:
            logger.error("Ошибка: Объект не найден.")
            return Response({"error": "Объект с указанным ID не найден."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductInfoCreateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except IntegrityError:
            logger.error("IntegrityError: Дублирующая запись для ProductInfo при обновлении.")
            return Response({"error": "Эта информация о продукте уже существует для данного продукта и магазина."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}")
            return Response({"error": "Произошла ошибка при обновлении данных."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ParameterViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    filterset_fields = ['id', 'name']
    
    def get_permissions(self):
        return self.get_permissions_mixin()

class ProductParameterViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = ProductParameter.objects.all()
    serializer_class = ProductParameterSerializer
    filterset_fields = ['id', 'product_info', 'parameter', 'value']
    
    def get_permissions(self):
        logger.info(f"Пользователь {self.request.user} пытается получить доступ к действию: {self.action}")
        
        if self.check_admin():
            return [AllowAny()]
        
        if self.action in self.allowed_actions_permission():
            return [AllowAny()]
        
        if self.check_user_type('supplier'):
            product_info_id = self.request.data.get('product_info')
            
            if product_info_id is None:
                logger.warning("product_info не передан в запросе.")
                raise PermissionDenied("Нет прав.")
            
            try:
                product_info = ProductInfo.objects.get(id=product_info_id)
            except ProductInfo.DoesNotExist:
                logger.error(f"ProductInfo с ID {product_info_id} не найден.")
                raise PermissionDenied("ProductInfo не найден.")
            
            if self.check_creator(product_info.id):
                logger.info("Доступ предоставлен: пользователь является создателем продукта.")
                return [AllowAny()]
        
        logger.warning(f"Доступ отклонен: у пользователя {self.request.user} нет прав для действия '{self.action}'.")
        raise PermissionDenied("Нет прав.")
    
    
class UploadFileView(PermissionMixin, APIView):
    def post(self, request):
        logger.info(not self.check_admin())
        
        if not self.check_admin() and not self.check_user_type('supplier'):
            logger.info('Нет прав.')
            return PermissionDenied('Нет прав.')

        file = request.FILES.get('file')
        if not file:
            return Response({"error": "Файл не найден"}, status=status.HTTP_400_BAD_REQUEST)

        logger.info('Файл найден')
        try:
            data = yaml.safe_load(file.read())
            self.process_categories(data.get('categories', []))
            shop_id = data.get('shop', [{}])[0].get('id')
            logger.info(f'магазин из файла : {shop_id}')

            if self.check_admin() or self.is_supplier_authorized(shop_id):
                self.process_products(data.get('goods', []), shop_id)
                return Response({"message": "Файл успешно обработан."}, status=status.HTTP_201_CREATED)
            else:
                logger.info('Нет прав для доступа к этому магазину.')
                return Response({"error": "Нет прав для доступа к этому магазину."}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error({"error": str(e)})
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def process_categories(self, categories):
        for category_data in categories:
            category, created = Category.objects.get_or_create(
                id=category_data['id'], 
                defaults={'name': category_data['name']}
            )
            if created:
                logger.info(f'Создана новая категория : {category}.')
            else:
                logger.info(f'Эта категория уже существует : {category}.')

    def is_supplier_authorized(self, shop_id):
        shop = Supplier.objects.filter(id=shop_id).first()
        if shop and shop.id == self.request.user.supplier.id:
            return True
        return False

    def process_products(self, goods, shop_id):
        shop = Supplier.objects.filter(id=shop_id).first()
        if not shop:
            logger.info(f'Shop id {shop_id} не найден.')
            raise ValueError(f"Shop id {shop_id} не найден.")

        for product_data in goods:
            category = self.get_category(product_data['category'])
            product, created = Product.objects.get_or_create(name=product_data['name'], category=category)

            product_info = ProductInfo.objects.create(
                model=product_data['model'],
                external_id=product_data['id'],
                product=product,
                shop=shop,  
                quantity=product_data['quantity'],
                price=product_data['price'],
                price_rrc=product_data['price_rrc']
            )
            logger.info(f'Создана новая информация о продукте : {product_info}')
            self.process_product_parameters(product_info, product_data.get('parameters', {}))

    def get_category(self, category_id):
        try:
            return Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            logger.info(f"Категория с ID {category_id} не существует.")
            raise ValueError(f"Категория с ID {category_id} не существует.")

    def process_product_parameters(self, product_info, parameters):
        for param_name, param_value in parameters.items():
            parameter, created = Parameter.objects.get_or_create(name=param_name)
            ProductParameter.objects.create(
                product_info=product_info,
                parameter=parameter,
                value=param_value
            )
            
            
class TestErrorView(APIView):
    def get(self, request):
        raise Exception("This is a test exception for Rollbar!")