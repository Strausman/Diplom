from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CancelOrderView,
    ConfirmOrderView,
    ConfirmPaymentView,
    CreateCartView,
    GetCartView,
    GetCartsView,
    GetOrderDetailView,
    GetOrdersView,
    UpdateCartView,
    DeleteCartView,
    CreateCartProductView,
    UpdateCartProductView,
    DeleteCartProductView,
    UpdateOrderStatusView,
)

router = DefaultRouter()

urlpatterns = [
    path('api/v1/carts/', GetCartsView.as_view()),
    path('api/v1/carts/create/', CreateCartView.as_view()),
    path('api/v1/carts/<pk>/', GetCartView.as_view()),
    path('api/v1/carts/<pk>/update/', UpdateCartView.as_view()),
    path('api/v1/carts/<pk>/delete/', DeleteCartView.as_view()),
    path('api/v1/cart-products/', CreateCartProductView.as_view()),
    path('api/v1/cart-products/<pk>/update/', UpdateCartProductView.as_view()),
    path('api/v1/cart-products/<pk>/delete/', DeleteCartProductView.as_view()),
    path('api/v1/carts/<pk>/confirm/', ConfirmOrderView.as_view()),
    path('api/v1/carts/<pk>/cancel/', CancelOrderView.as_view()),
    path('api/v1/carts/<pk>/confirm-payment/', ConfirmPaymentView.as_view()),
    path('orders/', GetOrdersView.as_view()),
    path('orders/<pk>/', GetOrderDetailView.as_view()),
    path('orders/<pk>/update/', UpdateOrderStatusView.as_view()),
]