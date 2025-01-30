from django.http import HttpResponse
from django.shortcuts import render
from .models import CustomUser
from .serializers import CustomUserSerializer, CustomerSerializers, SupplierSerializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .models import Customer, Supplier
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.exceptions import PermissionDenied, ValidationError


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filterset_fields = ['id', 'username', 'email', 'user_type']
    
    def get_permissions(self):
        if self.request.user.is_staff:
            return [AllowAny()]
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    
    def list(self, request, *args, **kwargs):
        if self.request.user.is_staff:
            users = CustomUser.objects.all()
            serializer = self.get_serializer(users, many=True)  
            return Response(serializer.data)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        if self.request.user.is_staff:
            if user_id:
                try:
                    user = CustomUser.objects.get(id=user_id)
                    serializer = self.get_serializer(user)
                    return Response(serializer.data)
                except CustomUser.DoesNotExist:
                    return Response({'detail': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'detail': 'ID пользователя не предоставлен.'}, status=status.HTTP_400_BAD_REQUEST)
        if str(request.user.id) != str(user_id):
            raise PermissionDenied ('Вы не можете просматривать данные других пользователей.')
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        if self.request.user.is_staff:
            if user_id:
                try:
                    user = CustomUser.objects.get(id=user_id)
                    serializer = self.get_serializer(user, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True) 
                    
                    if 'avatar' in request.FILES:  
                        user.avatar = request.FILES['avatar']  
                        user.save()  # Добавлено
                        create_thumbnail.delay(user.avatar.path)  
                    
                    serializer.save()
                    return Response(serializer.data)
                except CustomUser.DoesNotExist:
                    return Response({'detail': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)
                except ValidationError as e:
                    return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'ID пользователя не предоставлен.'}, status=status.HTTP_400_BAD_REQUEST)

        if str(request.user.id) != str(user_id):
            raise PermissionDenied('Вы не можете редактировать данные других пользователей.')

        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True) 
            serializer.save()
            
            # Обработка загрузки аватара
            if 'avatar' in request.FILES:  
                request.user.avatar = request.FILES['avatar']  
                request.user.save()  
                create_thumbnail.delay(request.user.avatar.path)  
            
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        if self.request.user.is_staff:
            if user_id:
                try:
                    user = CustomUser .objects.get(id=user_id)
                    user.delete()
                    return Response({'detail': 'Пользователь удален.'}, status=status.HTTP_200_OK)
                except CustomUser .DoesNotExist:
                    return Response({'detail': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'ID пользователя не предоставлен.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if str(request.user.id) != str(user_id):
            raise PermissionDenied('Вы не можете удалять данные других пользователей.')

        request.user.delete()
        return Response({'detail': 'Ваша учетная запись удалена.'}, status=status.HTTP_200_OK)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializers
    permission_classes = [IsAdminUser]
    

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializers
    permission_classes = [IsAdminUser]