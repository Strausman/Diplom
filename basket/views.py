from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser  
from rest_framework.views import APIView
from .models import Cart, CartProduct
from .serializers import CartSerializer, CartProductSerializer
from django.core.mail import send_mail


class ConfirmOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            cart = Cart.objects.get(pk=pk)
            if request.user.is_staff or cart.customer == request.user:
                if cart.confirm_order():
                    send_mail(
                        'Подтверждение заказа',
                        'Ваш заказ подтвержден!',
                        'from@example.com',
                        [request.user.email],
                        fail_silently=False,
                    )
                    return Response(status=status.HTTP_200_OK)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except Cart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            cart = Cart.objects.get(pk=pk)
            if request.user.is_staff or cart.customer == request.user:
                if cart.cancel_order():
                    return Response(status=status.HTTP_200_OK)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except Cart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ConfirmPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            cart = Cart.objects.get(pk=pk)
            if request.user.is_staff or cart.customer == request.user:
                if cart.confirm_payment():
                    return Response(status=status.HTTP_200_OK)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except Cart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class CreateCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            cart = Cart.objects.get(pk=pk)
            if request.user.is_staff or cart.customer == request.user:
                serializer = CartSerializer(cart)
                return Response(serializer.data)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except Cart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class GetCartsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            carts = Cart.objects.all()
        else:
            carts = Cart.objects.filter(customer=request.user)
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)

class UpdateCartView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            cart = Cart.objects.get(pk=pk)
            if request.user.is_staff or cart.customer == request.user:
                serializer = CartSerializer(cart, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except Cart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class DeleteCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            cart = Cart.objects.get(pk=pk)
            if request.user.is_staff or cart.customer == request.user:
                cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except Cart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class CreateCartProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartProductSerializer(data=request.data)
        if serializer.is_valid():
            cart = Cart.objects.get(pk=request.data['cart'])
            if request.user.is_staff or cart.customer == request.user:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateCartProductView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            cart_product = CartProduct.objects.get(pk=pk)
            cart = cart_product.cart
            if request.user.is_staff or cart.customer == request.user:
                serializer = CartProductSerializer(cart_product, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except CartProduct.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class DeleteCartProductView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            cart_product = CartProduct.objects.get(pk=pk)
            cart = cart_product.cart
            if request.user.is_staff or cart.customer == request.user:
                cart_product.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_403_FORBIDDEN)
        except CartProduct.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        
class GetOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Cart.objects.filter(customer=request.user)
        serializer = CartSerializer(orders, many=True)
        return Response(serializer.data)
    
class GetOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = Cart.objects.get(pk=pk)
        serializer = CartSerializer(order)
        return Response(serializer.data)
    
class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        order = Cart.objects.get(pk=pk)
        order.cart_type = request.data['cart_type']
        order.save()
        return Response(status=status.HTTP_200_OK)